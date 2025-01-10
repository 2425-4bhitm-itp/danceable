#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

npm run tailwind
npm run build

docker build -t "frontend" -f docker/Dockerfile .

#docker run -p 4200:80 frontend
