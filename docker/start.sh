#!/usr/bin/env bash

../code/backend/build.sh
../code/frontend/build.sh

docker compose up --build
