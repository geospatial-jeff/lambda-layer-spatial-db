# AWS Lambda Spatial Database

I am an AWS Lambda native spatial database, allowing for vector data (currently polygons) to be packaged, queried, and distributed through AWS Lambda.  The database implements the [Google S2 Library](http://s2geometry.io/) with a [B-tree](https://pythonhosted.org/BTrees/) to perform fast spatial lookups and is managed by [ZODB](http://www.zodb.org/en/latest/index.html), a native object database for Python.

The database is packaged and deployed as an AWS Lambda Layer.  If the layer is publicly available, the database can be easily "imported" and queried by external Lambda Functions.  This library primarily provides a set of utilities for building, deploying, and querying lambda native spatial databases.


#### Installation
```
git clone https://github.com/geospatial-jeff/lambda-layer-spatial-db.git
cd lambda-layer-spatial-db
pip install -e .[dev]
```

The library also requires an installation of the Google S2 Library which is not available via pip.  See the Dockerfile for instructions on how to build the Google S2 library plus python bindings (via SWIG). 

#### QuickStart
Your database application is defined in the `lambda_db` directory.  The library provides several CLI scripts for building and deploying the database.

```
# Build database
lambda-db build /path/to/feature_collection.geojson

# Package database as Lambda Layer and upload to AWS LAmbda
lambda-db deploy -t <docker_tag>:latest --public
```

Reference the layer's ARN in our lambda function configuration and query the database.  The lambda function will return all features in our database which intersect the input geojson feature.

```python
import json
from db import Database

def spatial_query(event, context):

    with Database.load(read_only=True, deployed=True) as db:
        response = db.spatial_query(event['geoj'])

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
```

For a step-by-step guide on building your own lambda-native spatial database, check out the [docs](/docs/README.md).

#### TODOS

- Add support for point features.
- Add support for parallel spatial query.
- Shard database over multiple lambda layers.