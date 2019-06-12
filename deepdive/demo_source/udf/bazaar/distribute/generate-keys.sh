#!/usr/bin/env bash

if [ -d "./ssh" ]; then
    echo 'Directory ./ssh exists already. Abort.'
    echo 'If you would like to re-generate the keys, please remove ./ssh and try again.'
    exit 1
fi 

# install SSH keys
echo "Creating SSH keys"
rm -rf ./ssh
mkdir ./ssh
cd ./ssh

# generate private/public key pair
ssh-keygen -t rsa -b 2048 -f bazaar.key -N '' -C bazaar

# generate azure pem file from openssh private key
openssl req \
    -x509 \
    -days 365 \
    -nodes \
    -key bazaar.key \
    -out bazaar.pem \
    -newkey rsa:2048 \
    -subj "/"

# install (separate) management certificates for azure
openssl req -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:1024 \
    -keyout mycert.pem \
    -out mycert.pem \
    -subj "/" 

openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer

echo 'All keys have been generated and placed into ./ssh.'
echo '   ssh/bazaar.key is the private key used to log in to worker machines'
echo '   ssh/bazaar.key.pub is the corresponding public key in OpenSSH format (ec2)'
echo '   ssh/bazaar.pem is the corresponding public key in OpenSSL format (azure)'
echo '   ssh/mycert.cer is a management certificate used for azure only'
echo 'NOTE: If you would like to use Azure, you must upload ssh/mycert.cer via the "Upload" action of the "Settings" tab of the management portal.'

