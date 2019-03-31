#!/bin/bash

BASEDIR=$(dirname "$0")

pip install --user --upgrade oauth2client
pip install --user --upgrade google-api-python-client

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


cd "$BASEDIR"

git pull
python ./main/SyncBackup.py $INPUT_NAME