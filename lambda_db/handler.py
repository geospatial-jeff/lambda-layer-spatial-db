import json
from db import Database

def spatial_query(event, context):

    with Database.load(read_only=True, deployed=True) as db:
        response = db.spatial_query(event['geoj'])

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }