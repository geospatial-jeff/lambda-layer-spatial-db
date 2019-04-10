import os
import json
import subprocess

import click
from lambda_db.db import Database
from analyze import choose_res


@click.group()
def lambda_db():
    pass

@lambda_db.command(name="build")
@click.argument('feature_collection', type=click.File('r'))
def build(feature_collection):
    data = json.load(feature_collection)

    with Database.load() as db:
        db.load_features(data)

@lambda_db.command(name="deploy")
@click.option('tag', '-t', type=str)
@click.option('--public', default=False, type=bool)
def deploy(tag, public):
    # Build lambda layer with docker
    print("Building docker image")
    subprocess.call('docker build . -t {}'.format(tag), shell=True)

    print("Building lambda layer deployment package")
    subprocess.call('docker run --rm -v $PWD:/home/spatial-db -it {} package.sh'.format(tag), shell=True)

    with Database.load() as db:
        # Publish lambda layer
        print("Publishing lambda layer to AWS")
        lambda_layer = db.publish_lambda_layer(public=public)

        info = db.info()
        print(info)

@lambda_db.command(name="analyze")
@click.argument('feature_collection', type=click.File('r'))
@click.option('--optimize', '-o', default='size', type=str)
def analyze(feature_collection, optimize):
    data = json.load(feature_collection)
    choose_res(data, optimize)

@lambda_db.command(name="info")
def info():
    with Database.load() as db:
        print(json.dumps(db.info(), indent=2))