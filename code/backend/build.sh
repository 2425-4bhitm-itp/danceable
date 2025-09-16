#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn clean package -DskipTests

docker build -t backend:latest -f docker/Dockerfile .

docker tag backend:latest ghcr.io/2425-4bhitm-itp/backend:latest

docker push ghcr.io/2425-4bhitm-itp/backend:latest
