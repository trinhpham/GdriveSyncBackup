#!/bin/bash

BASEDIR=$(dirname "$0")

cd "$BASEDIR"

echo "Working at $BASEDIR | $(date)"

pip install --user -r requirements.txt

PARENT_FOLDER=$2
if [ -z "$PARENT_FOLDER" ]
then
    PARENT_FOLDER="."
fi

INPUT_NAME=$1
if ! [[ "$INPUT_NAME" == *\/* ]]
then
  INPUT_NAME=`find $PARENT_FOLDER -maxdepth 1 -name $INPUT_NAME`
fi

echo "Input: $INPUT_NAME"

git pull
python ./main/SyncBackup.py $INPUT_NAME