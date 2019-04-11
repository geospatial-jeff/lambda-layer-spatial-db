# Deploying Lambda-Spatial-DB

## Getting Started

If you haven't already, please read through the [database docs](db_schema.md)

#### 1. Setup.

```
git clone https://github.com/geospatial-jeff/lambda-layer-spatial-db.git
cd lambda-layer-spatial-db
pip install -e .[dev]
```

#### 2. Edit the database configuration in `lambda_db/config.yml`.

| Variable  |  Description  |
|---|---|
|  db_name  |  Name of database.  Also determines name of the Lambda Layer. |
|  min_res  |  Minimum S2 cell resolution used when generating cell coverages. |
|  max_res  |  Maximum S2 cell resolution used when generating cell coverages. |
|  limit  |  Maximum number of S2 cells generated in a single cell coverage. |
|  unique_id  |  Unique id field of database.  This is used to filter back along the one-to-many relationship to prevent returning duplicate results. |
| compress | Determines if items are compressed (gzip) before inserted into database |

You can create an optimized configuration for generating S2 cell coverages through the CLI.  The following function suggests `min_res`, `max_res`, and `limit` parameters for the input geojson while optimizing for disk space (the algorithm is based on geometry-level statistics such as area, perimeter etc.).  The command will also print out a variety of statistics about your data which can be used to inform your decision.

```
lambda-db analyze /path/to/feature_collection.geojson --optimize size
```

#### 3. Build the database.
Once the database configuration has been updated you can build your database using the CLI:
```
lambda-db build /path/to/feature_collection.geojson
```

When the code finishes, your database will be saved in the `lambda_db` folder.
```
lambda_db/database.fs
lambda_db/database.fs.index
lambda_db/database.fs.lock
lambda_db/database.fs.tmp
```

#### 4. Package the database as an AWS Lambda Layer and upload to AWS Lambda.
Once you've built the database you can generate an AWS Lambda Layer using the CLI:
```
lambda-db deploy -t <docker_tag>:latest --public
```
The above command will generate a lambda layer deployment package (`lambda_db/lambda-layer.zip`), upload the layer to AWS Lambda, and make the layer publicly available.

#### 5. Check out your database info.
When finished, the `lambda-db deploy` function used in the previous step will print information about your database deployment.  You can re-generate this information at any time using the `lambda-db info` CLI script.

#### 6. Deploy Lambda Function (optional)
Once you have deployed the lambda layer to AWS Lambda your database is fully deployed and can be queried by attaching the Lambda Layer to a Lambda Function.  The library provides a sample serverless deployment (`lambda_db/serverless.yml`) for testing out your database.  Update the function's layer ARN in `lambda_db/serverless.yml` and deploy the service with `sls deploy -v`.

You can query your database by passing a geojson feature (with polygon geometry) to your lambda function's `geoj` argument.