#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn clean package -Dquarkus.config.locations=./src/main/resources/application.properties

docker build -t "backend" -f docker/Dockerfile .