#!/bin/sh
# Parse sentences in parallel

set -eu

# Usage: this_script input_file parallelism input_batch_size

if [ "$#" -le 1 ]; then
  echo "Usage: $0 input_file parallelism [input_batch_size=1000] [sentence_words_limit=120]"
  exit
fi

for i in "$@"
do
case $i in
  -in=*|--input=*)
    INPUT_FILE="${i#*=}"
    shift
    ;;
  -p=*|--parallelism=*)
    PARALLELISM="${i#*=}"
    shift
    ;;
  -b=*|--batch-size=*)
    BATCH_SIZE="${i#*=}"
    shift
    ;;
    *)
    echo "NO MATCH"
    break
    ;;
esac
done

if [ -z "$INPUT_FILE" ]; then
  echo "Usage: $0 -i=input_file [--parallelism=PARALLELISM] [--batch-size=BATCH_SIZE ] <args for run.sh>"
  exit
fi

PARALLELISM=${PARALLELISM:-2}
BATCH_SIZE=${BATCH_SIZE:-1000}

echo "parallelism = $PARALLELISM"
echo "batch-size  = $BATCH_SIZE"

RUN_SCRIPT=`cd $(dirname $0)/; pwd`"/run.sh $@"
echo $RUN_SCRIPT
mkdir -p $INPUT_FILE.split
rm -f $INPUT_FILE.split/*

# Split the input file into subfiles
split -a 10 -l $BATCH_SIZE $INPUT_FILE $INPUT_FILE.split/input-

# Match all files in the split directory
find $INPUT_FILE.split -name "input-*" 2>/dev/null -print0 | xargs -0 -P $PARALLELISM -L 1 bash -c "${RUN_SCRIPT}"' -f "$0"'

echo "Output TSV files are in: $INPUT_FILE.split/*.parsed"
echo "To load them into the databse, run: cat $INPUT_FILE.split/*.parsed | psql YOUR_DB_NAME -c "'"COPY sentences FROM STDIN"'
