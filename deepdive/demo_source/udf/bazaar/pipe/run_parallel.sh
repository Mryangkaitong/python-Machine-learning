#!/usr/bin/env bash

# Parses documents in parallel.
#
# Input is a single file that contains one JSON record per line.
# Output is a single file that contains one JSON record per line.
#
# The number of records and their order is the same in input and output.
#
# Example:
# ./run_parallel.sh --input=INPUT.json --output=OUTPUT.json \
#                   --params='-v content -k doc_id -a ExtendedCleanHtmlStanfordPipeline'
#
# The following environment variables are used when available.
#   PARALLELISM (default 2)
#   BATCH_SIZE  (default 1000)

set -eu

for i in "$@"
do
case $i in
  -in=*|--input=*)
    INPUT_FILE="${i#*=}"
    shift
    ;;
  -out=*|--output=*)
    OUTPUT_FILE="${i#*=}"
    shift
    ;;
  -pa=*|--params=*)
    PARAMS="${i#*=}"
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
  --keepsplit)
    KEEP_SPLIT=true
    shift
    ;;
  --compress)
    COMPRESS_OUTPUT=true
    shift
    ;;
    *)
    echo "Ignoring parameter: $i"
    break
    ;;
esac
done

if [ -z "$INPUT_FILE" ]; then
  echo "Usage: $0 -in=INPUT.json [-out=OUTPUT.json] [--parallelism=PARALLELISM] \\"
  echo "                    [--batch-size=BATCH_SIZE ] --params='<args for run.sh>'"
  exit
fi

# Setting defaults
PARALLELISM=${PARALLELISM:-2}
BATCH_SIZE=${BATCH_SIZE:-1000}
PARAMS=${PARAMS:-}
KEEP_SPLIT=${KEEP_SPLIT:-false}
COMPRESS_OUTPUT=${COMPRESS_OUTPUT:-false}
if [ "$COMPRESS_OUTPUT" = false ]; then
    OUTPUT_FILE=${OUTPUT_FILE:-$INPUT_FILE.out}
else
    OUTPUT_FILE=${OUTPUT_FILE:-$INPUT_FILE.out.gz}
fi

echo "parallelism = $PARALLELISM"
echo "batch-size  = $BATCH_SIZE"
echo "compress    = $COMPRESS_OUTPUT"

# Fixed a bug when "config.properties" does not exists
touch config.properties

RUN_SCRIPT=`cd $(dirname $0)/; pwd`"/run.sh --formatIn json --formatOut json $PARAMS"
echo $RUN_SCRIPT

SPLIT_DIR=$INPUT_FILE.split
mkdir -p $SPLIT_DIR
rm -rf $SPLIT_DIR/*

# Split the input file into subfiles
split -a 10 -l $BATCH_SIZE $INPUT_FILE $SPLIT_DIR/input-

# Match all files in the split directory
find $INPUT_FILE.split -name "input-*" 2>/dev/null -print0 | xargs -0 -P $PARALLELISM -L 1 bash -c "${RUN_SCRIPT}"' -i "$0" -o "$0.out"'

function merge_json_format {
    SPLIT_DIR=$1
    OUTPUT_FILE=$2
    # merging json files
    for file in $SPLIT_DIR/*.out
    do
        if [ "$COMPRESS_OUTPUT" = false ]; then
            cat $file >> $OUTPUT_FILE
        else
            cat $file | gzip >> $OUTPUT_FILE
        fi
    done
}


function merge_column_format {
    SPLIT_DIR=$1
    OUTPUT_FILE=$2
    # merging column format segments

    OUTDIR=$INPUT_FILE.out
    if [ -d "$OUTDIR" ]; then
        echo "$OUTDIR already exists. Aborting."
        exit 1
    fi
    mkdir $OUTDIR

    # first we determine the different annotators by looking at only one segment
    annotations=()
    for file in $SPLIT_DIR/*
    do
        if [[ -d $file ]]; then
            for ann in $file/*
            do
                annotations+=("${ann##*.}")
            done
            break
        fi
    done

    # now cat them all together
    for file in $SPLIT_DIR/*
    do
        if [[ -d $file ]]; then
            for ann in "${annotations[@]}"
            do
                cat $file/ann.$ann >> $OUTDIR/ann.$ann
            done
        fi
    done
}

merge_json_format $SPLIT_DIR $OUTPUT_FILE

# remove split dir
if [ "$KEEP_SPLIT" = false ]; then
    rm -rf $SPLIT_DIR
fi

echo "The output is in $OUTPUT_FILE"
