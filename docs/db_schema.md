# Database Docs

## Getting Started
The database supports ingseting geojson feature collections (currently polygons only) through the `lambda-db build path/to/data.geojson` CLI command.  The database expects input features to be projected to WGS84 (EPSG:4326).

## Spatial Indexing
The database uses Google's S2 Geometry Library as a spatial index.  The index is unique in that it indexes across a three-dimensional coordinate system as opposed to the projected coordinate systems used by traditional spatial indices.  The result is a singular spatial index which minimizes distortion across the entire Earth's surface.  S2 works by projecting each point onto a space-filling Hilbert curve which serializes space into a single dimension and allows for fast spatial lookups via range queries (which works great with a B-tree).

The S2 Geometry Library represents the Earth in a hierarchy of [S2 Cells](http://s2geometry.io/resources/s2cell_statistics).  There are 30 levels in the hierarchy containing smaller and smaller cells.  At the lowest level, the entire Earth is covered by only 6 cells while the highest level has 700,000,000 cells with an average area of 0.74 square centimeters.  S2 represents polygons by generating a "covering" of S2 cells which continuously fill the polygon ([interactive example](https://s2.sidewalklabs.com/regioncoverer/)).  The region-covering algorithm used by S2 allows the user to change the minimum and maximum levels of cells in the covering as well as the maximum number of allowable cells.

## Data Ingest
When a geojson feature collection is ingested into the database, a coverage of S2 cells is ingested for each polygon in the feature collection.  This means that there is a one-to-many relationship between the number of features and the number of items created in the database.  The output of the region-covering algorithm are heavily influenced by the three configuration parameters (`min_res`, `max_res`, and `limit`).  It is important that appropriate parameters are chosen given the properties of the input data.  The library provides a CLI command for optimizing region-covering configuration parameters (`lambda-db analyze path/to/data.geojson`).


## Schema
ZODB is compatible with several types of B-trees which implement both integer and object based mappings.  An integer key would be ideal, but ZODB only supports 32-bit integer keys while S2 creates 64-bit integers, so the database uses an object key.  The database uses an object value as well, which is generated by essentially calling `json.dumps()` on the `properties` key of the geojson feature.  As such, the database uses Python's [OOBTree implementation](https://pythonhosted.org/BTrees/).  An entry in the database representing a single cell from a geojson feature covering, in pseudocode, looks like this:

```json
{<s2_cell_id>: geojson['properties']
```

## Spatial Query
The query mechanism falls into the category of "embaressingly parallel" workflows; but due to the lambda execution environment, the database must be accessed in ["read-only" mode](http://www.zodb.org/en/latest/reference/storages.html#filestorage) which limits database access to one process.  This performing the range queries in parallel within a single lambda function.  Because the database is distributed as a Lambda Layer, and each function inherits its own fresh copy of the layer, it is possible (currently not implemented) to process the range queries in parallel across multiple lambda executions.