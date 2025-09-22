#!/bin/bash

# Build script for Angular frontend
set -e  # Exit on any error

echo "Starting Angular frontend build..."

# Navigate to frontend directory
cd ..
cd frontend

echo "Installing npm dependencies..."
npm ci


echo "Building Angular application for production..."
npm run build --prod

echo "Build completed successfully!"
echo "Build artifacts are available in: dist/"

# Optional: Show build output
ls -la dist/
