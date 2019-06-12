#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"/..

# make sure we have Bazaar/Parser set up
: ${BAZAAR_HOME:=$PWD/udf/bazaar}
[[ -x "$BAZAAR_HOME"/parser/target/start ]] || (
    echo >&2 "Setting up Bazaar/Parser"
    if [ ! -d "$BAZAAR_HOME" ]; then
	    mkdir -p "$BAZAAR_HOME"
	    cd "$BAZAAR_HOME"
	    [[ -d .git ]] || git clone https://github.com/HazyResearch/bazaar.git .
        cd parser
    else
        cd "$BAZAAR_HOME"/parser
	fi
    
    : ${SBT_OPTS:=-Xmx1g}
    export SBT_OPTS
    ./setup.sh
)


