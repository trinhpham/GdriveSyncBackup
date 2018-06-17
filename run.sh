#!/bin/bash

BASEDIR=$(dirname "$0")
cd "$BASEDIR"

git pull

python ./main/SyncBackup.py $1