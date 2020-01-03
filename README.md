# Overview
This repo contains a demo for using Redis (in a Docker container or on ElastiCache) as a caching layer for a MySQL database. The demo does not require AWS and can be run locally as well as in the cloud. 

This demo showcases the performance improvements that can be achieved when using Amazon ElastiCache for Redis to accelerate relational (MySQL) database queries.

**Warning: The application and instructions were developed and tested on a Mac client and an EC2 Amazon Linux server.**

# How it works
The demo is a single page web application ([SPA](https://en.wikipedia.org/wiki/Single-page_application)) that performs semi-random queries on a MySQL database and caches results in Redis. It then collects stats on performance of cache vs. the database. 

The demo is implemented in [Python Flask](https://www.fullstackpython.com/flask.html) (backend) and Javascript on a client HTML page. The demo runs in a Docker container to make dependencies easier to manage.

The application queries the MySQL database for a 1000 times, each query will use a random number of records to fetch back. Query results will be returned from Redis if in cache or returned from the DB if not.

**Note:** The application leverages 2 Redis endpoints, a master endpoint to write to and a read replica endpoint to read the statistics for query performance. The application will not be able to refresh the UX if the same endpoint is used for both reads and writes due to the single-threaded, blocking nature of Redis.

# How to use it
Once installed, browse to the root application web address and click the **Query DB** button. The application will then run 1,000 queries against the cache / database and display the number of cache hits and misses on Redis. The last call duration is displayed inside the bar graph.

![Screenshot]
(https://github.com/nirmash/ElastiCache_DbCache_Demo/blob/master/images/dbcache_screen.jpg?raw=true)


# Install
This demo can run on a local environment that uses Docker or on EC2 with ElastiCache for Redis. 
## Prerequisites 
The application dependencies are valid for both local environments or on EC2:
* [Docker](https://docs.docker.com/v17.09/engine/installation/)
* [docker-compose](https://docs.docker.com/compose/install/)
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

**Note:** `yum` is the package manager used on EC2 Amazon Linux instances.
## Setup the MySQL database 

## Application files
Clone the demo repository:
```
$ git clone https://github.com/nirmash/ElastiCache_DbCache_Demo.git
```
Set the environment variables required to run the demo. 

```
export REDIS_MASTER_HOST=your_redis_master_node_endpoint
export REDIS_READER_HOST=your_redis_replica_node_endpoint      
export REDIS_MASTER_PORT=your_redis_master_port (typically 6379)
export REDIS_READER_PORT=your_redis_replica_port (typically 6379)      
export HOST=your_mysql_endpoint
export PASS=your_mysql_password
export USER=your_mysql_username
```
**Note:** The demo uses environment variables to store application secrets.


# Run
Browse to the `docker-compose.yaml` file location and load the application Docker container:
```
$ cd ElastiCache_DbCache_Demo/dbcache
$ ./init_service.sh
```
After the build process is done, the Docker containers status will appear (see below):

```
      Name                     Command               State                 Ports               
-----------------------------------------------------------------------------------------------
dbcache_redis_1     docker-entrypoint.sh redis ...   Up      0.0.0.0:63791->6379/tcp, 63791/tcp
dbcache_replica_1   docker-entrypoint.sh redis ...   Up      0.0.0.0:63790->6379/tcp           
dbcache_service_1   /bin/sh -c /code/run-server.sh   Up      10000/tcp, 0.0.0.0:80->80/tcp    
```
Note that the application will load 3 containers, the dbcache_service_1 contains the application code while the 2 Redis containers can be used instead of ElastiCache to run the demo locally.

# Troubleshoot

 
 	
