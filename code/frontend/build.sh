#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

npm install
npm run tailwind
npm run build

docker build -t "frontend" -f docker/Dockerfile .
