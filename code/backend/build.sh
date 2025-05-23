#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

mvn clean install -DskipTests -Dquarkus.config.locations=./src/main/resources/application.properties

