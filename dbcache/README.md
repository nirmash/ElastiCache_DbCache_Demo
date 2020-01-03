# Build the initial cluster with the envoy
https://www.envoyproxy.io/docs/envoy/latest/start/sandboxes/redis#running-the-sandboxes
$ pwd
envoy/examples/redis
$ docker-compose pull
$ docker-compose up --build -d
$ docker-compose ps
# Login to the envoy docker machine 
docker exec -it redis_service_1  /bin/bash
# Create a replica for the 1st master 
docker exec -it redis_service_1 redis-cli -h redis_replica_1 -p 6379 replicaof redis_redis_1 6379
docker exec -it redis_service_1 redis-cli -h redis_replica_1 -p 6379 config set slave-read-only no
docker exec -it redis_service_1 /bin/bash

# Test 
redis-cli -h localhost -p 1999 set foo bar
docker network inspect redis_envoymesh
docker exec -it dbcache_service_1 /bin/bash

curl http://localhost/service/set/new_route

curl http://localhost/service/set/run_route/

# Delete the DB
docker exec -it redis_redis_1 /bin/bash
FLUSHDB

docker exec -it redis_replica_1 /bin/bash
FLUSHDB

# Data Structures
Number of trips
Max time
Avg time 
Min time 
Longest 
Shortest
Trip summary

 
 	
