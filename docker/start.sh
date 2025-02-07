#!/usr/bin/env bash

BUILD=true
DEPLOY=true

while [ "$#" -gt 0 ]; do
    case "$1" in
        -sb|--skip-build) BUILD=false ;;
        -sd|--skip-deploy) DEPLOY=false ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "  -sb, --skip-build       Skip building code and images"
            echo "  -sd, --skip-deploy      Skip deploying containers"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if [ "$BUILD" = true ]
then
  echo "Building backend..."
  ../code/backend/build.sh || { echo "Backend build failed!"; exit 1; }

  echo "Building frontend..."
  ../code/frontend/build.sh || { echo "Frontend build failed!"; exit 1; }

  echo "Building machine learning service..."
  ../code/ml/build.sh || { echo "ML build failed!"; exit 1; }
fi;

if [ "$DEPLOY" = true ]
then
  echo "Starting Docker services..."
  docker compose up --build

  if [ $? -ne 0 ]; then
    echo "Failed to start Docker services!"
    exit 1
  fi
fi;