#!/usr/bin/env bash

../code/backend/build.sh
../code/frontend/build.sh
../code/ml/build.sh

docker compose -f docker-compose.networks.yaml -f database.yaml -f backend.yaml -f frontend.yaml -f ml.yaml up --build