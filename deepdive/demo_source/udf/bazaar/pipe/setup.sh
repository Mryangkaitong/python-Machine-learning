#!/bin/bash

DIRNAME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# fetch SR models
DESTDIR=$DIRNAME/lib
FILENAME='stanford-srparser-2014-10-23-models.jar'
if [ ! -e "$DESTDIR/$FILENAME" ]; then
    mkdir -p $DESTDIR
    wget -P $DESTDIR http://nlp.stanford.edu/software/stanford-srparser-2014-10-23-models.jar
else
    echo "Skipping download: $DESTDIR/$FILENAME already exists"
fi

# On Ubuntu, install java 8
#sudo add-apt-repository -y ppa:openjdk-r/ppa
#sudo apt-get update
#sudo apt-get install -y openjdk-8-jdk

# build parser
cd $DIRNAME
sbt/sbt stage

