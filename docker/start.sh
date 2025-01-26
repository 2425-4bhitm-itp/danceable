#!/usr/bin/env bash

# Define the required Docker network name
NETWORK_NAME=my-network

# Check if the Docker network exists; if not, create it
if ! docker network ls | grep -q "$NETWORK_NAME"; then
  echo "Network $NETWORK_NAME does not exist. Creating it now..."
  docker network create $NETWORK_NAME
else
  echo "Network $NETWORK_NAME already exists."
fi

# Build the backend, frontend, and machine learning components
echo "Building backend..."
../code/backend/build.sh || { echo "Backend build failed!"; exit 1; }

echo "Building frontend..."
../code/frontend/build.sh || { echo "Frontend build failed!"; exit 1; }

echo "Building machine learning service..."
../code/ml/build.sh || { echo "ML build failed!"; exit 1; }

# Start the Docker services with the specified compose files
echo "Starting Docker services..."
docker compose \
  -f docker-compose.networks.yaml \
  -f database.yaml \
  -f backend.yaml \
  -f frontend.yaml \
  -f ml.yaml \
  up --build

# Check if docker-compose command succeeded
if [ $? -eq 0 ]; then
  echo "Docker services started successfully."
else
  echo "Failed to start Docker services!"
  exit 1
fi
