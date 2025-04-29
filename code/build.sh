#!/usr/bin/env bash

# shellcheck disable=SC2164
#cd "$(dirname "$0")"

set -e

pushd ./backend
./build.sh
popd

pushd ./frontend
./build.sh
popd