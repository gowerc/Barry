#!/bin/bash

## Get script directory
BARRY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

## Setup path to Python
PYTHON=$BARRY_DIR/venv/bin/python

##  Expand script name, extension and basename
SCRIPT=$1

## Generate log directory name
LOG_FILE=$BARRY_DIR/logs/$SCRIPT-$(date +\%Y-\%m-\%d).log

## Run script outputting to logfile 
$PYTHON  $BARRY_DIR/Barry.py $SCRIPT > $LOG_FILE 2>&1

