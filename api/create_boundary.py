import json
import boto3
import uuid
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

def render(status_code, text=None, content=None):
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": json.dumps({"message": text})
    }

def lambda_handler(event, context):
    try:
        name = event.get('name')

        if event.get('description') is not None:
            description = event.get('description')
        else:
            description = str()

        polygon = sevent.get('polygon')

        if event.get('resource_ids') is not None:
            resource_ids = event.get('resource_ids')
        else :
            resource_ids = list()

        if event.get('metadata') is not None:
            metadata = event.get('metadata')
        else:
            metadata = dict()

        event_log = list()
        time = str(datetime.now())

        boundary_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
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
        return render(200, text="OK")
    except Exception as e:
        return render(400, text="Invalid Syntax")
