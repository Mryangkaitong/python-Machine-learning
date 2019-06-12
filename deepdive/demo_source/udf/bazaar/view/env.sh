# elasticsearch
export INDEX_NAME=view

# database
export PGPORT=5432
export PGHOST=localhost
export DBNAME=deepdive_spouse_tsv
export PGUSER=raphael
export PGPASSWORD=

source env/bin/activate

PATH="$PWD/node_modules/.bin:$PATH"
PATH="$PWD/util/elasticsearch-1.6.0/bin:$PATH"
