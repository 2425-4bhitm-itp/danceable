#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn -B clean package -DskipTests

docker build -t "backend" -f docker/Dockerfile .
