#!/usr/bin/env bash

# install virtualenv
command -v virtualenv >/dev/null 2>&1 || {
  echo >&2 "virtualenv required but not installed. Aborting.";
  echo >&2 "You can install virtualenv with:"
  echo >&2 "    sudo pip install virtualenv"
}

virtualenv env
source env/bin/activate

pip install azure
pip install botocore
pip install fabric
pip install urltools

