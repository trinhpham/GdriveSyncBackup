#!/bin/bash

BASEDIR=$(dirname "$0")
cd "$BASEDIR"

git pull

pip install --user --upgrade oauth2client
pip install --user --upgrade google-api-python-client

INPUT_NAME=$@
if ! [[ "$INPUT_NAME" == *\/* ]]
then
  INPUT_NAME=`find . -maxdepth 1 -name $INPUT_NAME`
fi

python ./main/SyncBackup.py $INPUT_NAME