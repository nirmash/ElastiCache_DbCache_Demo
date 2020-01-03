# Overview
This repo contains a demo for using Redis (in a Docker container or on ElastiCache) as a caching layer for a MySQL database. The demo does not require AWS and can be run locally as well as in the cloud. 

# How it works
The demo is a single page web application ([SPA](https://en.wikipedia.org/wiki/Single-page_application)) that performs semi-random queries on a MySQL database and caches results in Redis. It then collects stats on performance of cache vs. the database. 

The demo is implemented in [Python Flask](https://www.fullstackpython.com/flask.html) (backend) and Javascript on a client HTML page. The demo runs in a Docker container to make dependencies easier to manage.

The application queries the MySQL database for a 1000 times, each query will use a random number of records to fetch back. Query results will be returned from Redis if in cache or returned from the DB if not.

# How to use it
Once installed, browse to the root application web address and click the **Query DB** button. The application will then run 1,000 queries against the cache / database and display the number of cache hits and misses on 

[default screen]:(images/dbcache_screen.jpg)


# Install

# Run

# Troubleshoot

 
 	
