#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn clean package

docker build -t "backend" -f docker/Dockerfile .

#docker run -p 8080:80 backend