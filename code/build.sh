#!/usr/bin/env bash

# shellcheck disable=SC2164
#cd "$(dirname "$0")"



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