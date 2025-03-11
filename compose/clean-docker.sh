#!/usr/bin/env bash

docker container prune -f
docker image prune -f
docker volume prune -f
docker builder prune --all --force
IMAGES=$(docker images -q)

for image in $IMAGES
do
    docker image rm -f $image
done
VOLUMES=$(docker volume ls -q)
for volume in $VOLUMES
do
    docker volume rm $volume 
done
docker container ls
docker volume ls
docker image ls
