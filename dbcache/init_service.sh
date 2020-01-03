#!/bin/sh
docker-compose stop
docker-compose pull
docker-compose up --build -d
docker exec -it dbcache_service_1 redis-cli -h dbcache_replica_1 -p 6379 replicaof dbcache_redis_1 6379
docker exec -it dbcache_service_1 redis-cli -h dbcache_replica_1 -p 6379 config set slave-read-only no
docker-compose ps