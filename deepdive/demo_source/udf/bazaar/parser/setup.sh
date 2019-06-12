#!/bin/bash

set -e

DIRNAME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# fetch SR models
DESTDIR="$DIRNAME"/lib
FILENAME='stanford-srparser-2014-10-23-models.jar'
if [ ! -e "$DESTDIR/$FILENAME" ]; then
    mkdir -p "$DESTDIR"
    url="http://nlp.stanford.edu/software/stanford-srparser-2014-10-23-models.jar"
    if type wget &>/dev/null; then
        wget -P "$DESTDIR" "$url"
    elif type curl &>/dev/null; then
        ( cd "$DESTDIR" && curl -LO "$url" )
    else
        echo >&2 "Could not find curl or wget.  Manually download $url to $DESTDIR/"
        false
    fi
else
    echo "Skipping download: $DESTDIR/$FILENAME already exists"
fi

# java
#sudo add-apt-repository -y ppa:openjdk-r/ppa
#sudo apt-get update
#sudo apt-get install -y openjdk-8-jdk

# check if java -version >= 1.8
javaVersion=$(java -version 2>&1 | sed -e '1!d; s/^java version "//; s/"$//')
[[ ! $javaVersion < 1.8 ]] || {
    echo >&2 "java -version >= 1.8 required but found: $javaVersion"
    false
}

# build parser
cd "$DIRNAME"
sbt/sbt stage

