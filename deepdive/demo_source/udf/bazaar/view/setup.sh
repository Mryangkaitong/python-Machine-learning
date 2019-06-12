#!/usr/bin/env bash

# install virtualenv
command -v virtualenv >/dev/null 2>&1 || {
  echo >&2 "virtualenv required but not installed. Aborting.";
  echo >&2 "You can install virtualenv with:"
  echo >&2 "    sudo pip install virtualenv"
}

virtualenv env
source env/bin/activate

# install python dependencies
pip install elasticsearch
pip install pyhocon
pip install psycopg2

# install node packages
npm install

# elasticsearch
cd util
ES_VER=elasticsearch-1.6.0
if [ ! -f ${ES_VER}.tar.gz ]; then
    curl -L -O https://download.elastic.co/elasticsearch/elasticsearch/${ES_VER}.tar.gz
    tar xvzf ${ES_VER}.tar.gz
fi
# must add
echo "script.disable_dynamic: false" >> ${ES_VER}/config/elasticsearch.yml
cd ..

# for development, we would like to enable auto-reload
npm install react-tools nodemon

cd public
git clone https://github.com/google/closure-library


