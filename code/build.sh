#!/usr/bin/env bash

set -e

pushd ./backend
chmod +x build.sh
./build.sh
popd

pushd ./frontend
chmod +x build.sh
./build.sh
popd

pushd ./angular-frontend
chmod +x build.sh
./build.sh
popd