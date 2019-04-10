import json

import click
from db import Database
from analyze import choose_res


@click.group()
def lambda_db():
    pass


@lambda_db.command(name="build")
@click.argument('db_path')
@click.argument('feature_collection', type=click.File('r'))
def build(db_path, feature_collection):
    data = json.load(feature_collection)

    with Database.load(db_path) as db:
        db.load_features(data)

@lambda_db.command(name="analyze")
@click.argument('feature_collection', type=click.File('r'))
@click.option('--optimize', '-o', default='size', type=str)
def analyze(feature_collection, optimize):
    data = json.load(feature_collection)
    choose_res(data, optimize)