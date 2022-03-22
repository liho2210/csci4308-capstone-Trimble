import json
import boto3
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

def lambda_handler(event, context):
    valid = True
    time = str(datetime.now())
    description=''
    resource_ids=[]
    event_log=[]
    metadata=str({})
    #required field
    if event['name']:
        name = event['name']
    else:
        valid = False

    if event['description']:
        description = event['description']

    #required field
    if event['polygon']:
        polygon=[]
        for coord in event['polygon'] :
            polygon.append(str(coord))
    else :
        valid = False

    if event['resource_ids']:
        resource_ids = event['resource_ids']

    if event['metadata']:
        metadata = event['metadata']

    if valid:
        boundary_table.put_item(
            Item={
                'id': name + "-" + time,
                'name': name,
                'description': description,
                'polygon': polygon,
                'resource_ids': resource_ids,
                'metadata': metadata,
                'event_log': event_log,
                'date_created': time,
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
