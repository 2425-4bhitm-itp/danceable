#!/usr/bin/env bash

set -e
# shellcheck disable=SC2164
#cd "$(dirname "$0")"

npm install
npm run build
