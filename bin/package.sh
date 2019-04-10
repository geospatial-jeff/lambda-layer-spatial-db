#!/bin/bash

export DEPLOY_DIR=layer
PYPATH=/var/lang/lib/python3.6/site-packages
DB_DIR=lambda_db
DBNAME=database

echo Creating deploy package

mkdir $DEPLOY_DIR
mkdir $DEPLOY_DIR/lib

# copy libs
cp -P /usr/local/lib/libs2.so $DEPLOY_DIR/lib
strip $DEPLOY_DIR/lib/* || true

# Moving python libraries
mkdir $DEPLOY_DIR/python
EXCLUDE="urllib3* s3transfer* boto3* botocore* pip* docutils* *.pyc setuptools* wheel* coverage* testfixtures* mock* *.egg-info *.dist-info __pycache__ easy_install.py"

EXCLUDES=()
for E in ${EXCLUDE}
do
    EXCLUDES+=("--exclude ${E} ")
done

rsync -ax $PYPATH/ $DEPLOY_DIR/python/ ${EXCLUDES[@]}

# Moving Google S2 Library
cp /build/s2geometry/build/python/* $DEPLOY_DIR/python/

# Packaging database
mkdir $DEPLOY_DIR/share
cp $DB_DIR/$DBNAME.fs $DEPLOY_DIR/share/
cp $DB_DIR/$DBNAME.fs.lock $DEPLOY_DIR/share/
cp -r $DB_DIR/*.py $DEPLOY_DIR/python/

# zip up deploy package
cd $DEPLOY_DIR
zip -ruq ../lambda-layer.zip ./