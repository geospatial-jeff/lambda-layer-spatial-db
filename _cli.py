import json

import click
from db import Database


@click.group()
def lambda_db():
    pass


@lambda_db.command(name="build")
@click.argument('db_path')
@click.argument('geojson', type=click.File('r'))
def build(db_path, feature_collection):
    data = json.load(feature_collection)

    with Database.load(db_path) as db:
        db.load_features(data)
