import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

def lambda_handler(event, context):
    valid = True
    time = str(datetime.now())
    #required field
    if event['name']:
        name = event['name']
    else:
        valid = False

    if event['description']:
        description = event['description']

    #required field
    if event['polygon']:
        polygon = event['polygon']
    else :
        valid = False

    if event['resource_ids']:
        resource_ids = event['resource_ids']

    if event['metadata']:
        metadata = event['metadata']

    #Make sure they polygon is valid

    if valid:
        boundary_table.put_item(
            Item={
                'date_created': time,
                'name': name,
                'description': description,
                'polygon': polygon,
                'resource_ids': resource_ids,
                'metadata': metadata,
                'event_log': [],
                'last_modified': time
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('OK')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('INVALID SYNTAX')
        }
