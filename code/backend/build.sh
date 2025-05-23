#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn clean install -Dquarkus.config.locations=./src/main/resources/application.properties

