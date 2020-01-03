from flask import render_template
from flask import Flask
from flask import request
from flask import make_response, jsonify
from json import JSONEncoder
import threading
import json
import random
import os
import redis
import requests
import socket
import sys
import uuid
import time
import pickle
import pymysql, datetime, hashlib


from dbcache import app, get_redis_client, get_redis_reader_client

m = None                  # MySQL connection
r = None                  # Redis connection
start_time_value = None   # Used to track start time of remote call
TTL = 5000                # In milliseconds, so 5 seconds
redis_counter = 0         # Track the number of Redis GETs
mysql_counter = 0         # Track the number of MySQL SELECTs
mysql_time = 0            # Total milliseconds accrued by MySQL
redis_time = 0            # Total milliseconds accrued by Redis
hits_counter = 0
key_prefix = "ex4:"

@app.route('/start_db_run')
def start_db_run():
  connect_databases()
  threading.Thread(target=loadDbData).start()
  return make_response('ok',200)

@app.route('/get/db_run_sums')
def get_db_run_sums():
  connect_databases()
  summary = redis_reader_con.get('DBSUMMARY')
  if not summary:
    return make_response('still running',200)
  return make_response(summary,200)

@app.route('/get/db_cache')
def get_db_cache():
  connect_databases()
  hits = int(redis_reader_con.get('db_cache_hit_counter'))
  miss = int(redis_reader_con.get('db_cache_miss_counter'))
  res = make_response(jsonify('{}|{}'.format(hits,miss)),200)
  return res

@app.route('/get/log/<LogId>')
def get_logs(LogId):
  connect_databases()
  log = get_redis_client().lrange('WORKER_{}'.format(LogId), 0, 25)
  if not log:
    return(make_response('',200))
  res = make_response(make_json_from_redis(log), 200)
  return res

@app.route('/get/latest_time')
def get_times():
  connect_databases()
  tRedis = float(redis_reader_con.get('db_cahce_redis_time'))
  tMySQL = float(redis_reader_con.get('db_cahce_mysql_time'))
  res = make_response(jsonify('{}|{}'.format(tRedis,tMySQL)),200)
  return res

def make_json_from_redis(objs):
  lst = [] 
  for obj in objs:
    lst.append(obj)
  return json.dumps(lst)

def print_summary():

    global redis_counter, mysql_counter, redis_time, mysql_time
    mysql_avg_ms = mysql_time / mysql_counter
    redis_avg_ms = redis_time / redis_counter
    delta = mysql_avg_ms / redis_avg_ms
    header = '       {: ^6s}  {: ^6s}'
    entry  = '{:5s}  {:>6,d}  {:6.2f}'
    print('')
    print (header.format('Calls', 'Avg ms'))
    print (header.format('======', '======'))
    print (entry.format('MySQL', mysql_counter, mysql_avg_ms))
    print (entry.format('Redis', redis_counter, redis_avg_ms))
    print ('\nRedis was about {:5,d} times faster\n'.format(int(delta)))
    sm = summary(mysql_counter,redis_counter,mysql_avg_ms,redis_avg_ms)
    r.set('DBSUMMARY',json.dumps(sm.__dict__))

def start_timer():

    global start_time_value
    start_time_value = datetime.datetime.now()

def end_timer():

    delta = datetime.datetime.now() - start_time_value
    return (delta.microseconds / 1000)

def connect_databases():

    global mySQL_con, redis_reader_con, redis_writer_con
    mySQL_con = pymysql.connect(
        os.getenv('HOST'),
        os.getenv('USER'),
        os.getenv('PASS'),
        os.getenv('DB'))

    redis_reader_con = get_redis_reader_client()
    redis_writer_con =  get_redis_client()

def fetch(sql):

    global mysql_time, redis_time, redis_counter, mysql_counter, hits_counter

    # Format the SQL string
    SQLCmd = sql.format(random.randrange(1,75))
    
    # Create unique hash key from query string
    hash = hashlib.sha224(SQLCmd.encode('utf-8')).hexdigest()
    key = key_prefix + hash

    # Gather timing stats while fetching from Redis
    start_timer()
    value = redis_reader_con.get(key)
    end_time = end_timer()
    redis_time = redis_time + end_time
    redis_counter = redis_counter + 1

    if value is not None:
        # Result was in cache
        ql = query_line(SQLCmd,end_time,redis_counter,'hit')
        log_data(redis_writer_con, 'DBCACHE',ql)
        hits_counter = hits_counter + 1
        redis_writer_con.set('db_cahce_redis_time',end_time)
        redis_writer_con.incr('db_cache_hit_counter')
        return value
    else:
        # Get data from SQL
        start_timer()
        cursor=mySQL_con.cursor()
        cursor.execute(SQLCmd)
        value = cursor.fetchall()[0][0]
        end_time = end_timer()
        mysql_time = mysql_time + end_time
        mysql_counter = mysql_counter + 1
        ql = query_line(SQLCmd,end_time,mysql_counter,'miss')
        redis_writer_con.incr('db_cache_miss_counter')
        redis_writer_con.set('db_cahce_mysql_time',end_time)
        redis_writer_con.psetex(key, TTL, value)
        log_data(redis_writer_con, 'DBCACHE',ql)
        return value    

class query_line: 
  def __init__ (self,sql_txt,time,cnt,hm):
    self.sql_txt = sql_txt
    self.time = int(time) 
    self.cnt = int(cnt) 
    self.hm = hm

class summary: 
  def __init__ (self,sql_calls,redis_calls,sql_avg,redis_avg):
    self.sql_calls = sql_calls
    self.redis_calls = redis_calls 
    self.sql_avg = sql_avg
    self.redis_avg = redis_avg

def log_data(client, worker_id, data):
    log_line = json.dumps(data.__dict__)
    client.rpush('WORKER_{}'.format(worker_id), log_line)
    client.ltrim('WORKER_{}'.format(worker_id), -10, -1)

def clear_all_logs(client, worker_id):
    client.delete('WORKER_{}'.format(worker_id))
    client.delete('DBSUMMARY')
    client.set('db_cache_miss_counter',0)
    client.set('db_cache_hit_counter',0)
    client.set('db_cahce_mysql_time',0)
    client.set('db_cahce_redis_time',0)
    


def loadDbData():
    clear_all_logs(redis_writer_con,'DBCACHE')
    for _ in range(999):
        fetch(os.getenv('SQL_QUERY_TEXT'))
    print_summary()
    return
