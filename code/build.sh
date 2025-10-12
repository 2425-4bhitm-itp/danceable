#!/usr/bin/env bash

set -e

pushd ./backend
chmod +x build.sh
./build.sh
popd