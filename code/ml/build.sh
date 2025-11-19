#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

docker build -t "ml" -f docker/Dockerfile .
