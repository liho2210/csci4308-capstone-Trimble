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
    body = event['body']
    payload = json.loads(body)
    try:
        if payload.get('name') is not None:
            name = str(payload.get('name'))
        else:
            return render(400,text='Boundary must include name')

        if payload.get('description') is not None:
            description = str(payload.get('description'))
        else:
            description = str()

        if payload.get('polygon') is not None:
            polygon = str(payload.get('polygon'))
        else:
            return render(400,text='Boundary must include polygon')

        if payload.get('resource_ids') is not None:
            resource_ids = payload.get('resource_ids')
        else :
            resource_ids = list()

        if payload.get('metadata') is not None:
            metadata = payload['metadata']
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
        return render(500, text="Server Error")
