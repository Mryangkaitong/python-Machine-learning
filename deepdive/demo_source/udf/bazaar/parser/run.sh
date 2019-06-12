#! /usr/bin/env bash

export JAVA_OPTS="-Xmx4g -Dfile.encoding=UTF-8"

$(dirname $0)/target/start $@
