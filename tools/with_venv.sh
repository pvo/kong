#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.olympus-venv
source $VENV/bin/activate && $@
