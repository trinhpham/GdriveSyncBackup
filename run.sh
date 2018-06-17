#!/bin/bash

BASEDIR=$(dirname "$0")
cd "$BASEDIR"

git pull

pip install --upgrade oauth2client
pip install --upgrade google-api-python-client

python ./main/SyncBackup.py $@