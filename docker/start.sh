#!/usr/bin/env bash

echo "Building backend..."
../code/backend/build.sh || { echo "Backend build failed!"; exit 1; }

echo "Building frontend..."
../code/frontend/build.sh || { echo "Frontend build failed!"; exit 1; }

echo "Building machine learning service..."
../code/ml/build.sh || { echo "ML build failed!"; exit 1; }

echo "Starting Docker services..."
docker compose up --build

if [ $? -ne 0 ]; then
  echo "Failed to start Docker services!"
  exit 1
fi