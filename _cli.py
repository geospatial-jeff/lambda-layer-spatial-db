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
@click.option('--include-geometry/--no-geometry', default=False)
def build(feature_collection, include_geometry):
    data = json.load(feature_collection)

    # Move geometry to data
    if include_geometry:
        for feat in data['features']:
            feat['properties'].update({'geometry': feat['geometry']})

    with Database.load() as db:
        db.load_features(data)

@lambda_db.command(name="deploy")
@click.option('tag', '-t', type=str)
@click.option('--public/--not-public', default=False)
@click.option('--dry-run/--wet-run', default=False)
def deploy(tag, public, dry_run):
    # Build lambda layer with docker
    os.chdir(os.path.dirname(__file__))

    print("Building docker image")
    subprocess.call('docker build . -t {}'.format(tag), shell=True)

    print("Building lambda layer deployment package")
    subprocess.call('docker run --rm -v $PWD:/home/spatial-db -it {} package.sh'.format(tag), shell=True)

    if not dry_run:
        with Database.load() as db:
            # Publish lambda layer
            print("Publishing lambda layer to AWS")
            db.publish_lambda_layer(public=public)

            print(json.dumps(db.info(), indent=2))
    else:
        print("dry-run flag is enabled, layer has not been published to AWS")

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