import json
import boto3
import uuid
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
event_table = dynamodb.Table('event')


def render(status_code, text=None, content=None):
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": content if content else json.dumps({"message": text})
    }


def insert_data(payload):
    try:
        event_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'zone_id': payload.get('zone_id'),
                'boundary_name': payload.get('boundary_name'),
                'resource_name': payload.get('resource_name', ''),
                'prev_resource_status': payload.get('prev_resource_status', ''),
                'curr_resource_status': payload.get('resource_status'),
                'description': payload.get('description', ''),
                'time_created': str(datetime.now()),
                'metadata': payload.get('metadata', {})
            }
        )

    except Exception as e:
        raise Exception(e)

    return (200, 'OK')


def sns(payload):
    client = boto3.client('sns')
    message = ''
    if payload.get('prev_resource_status'):
        message = payload['resource_name'] + ' resource status has been changed from ' + payload[
            'prev_resource_status'] + ' to ' + payload['resource_status']
    else:
        message = payload['resource_name'] + ' resource status is ' + payload['resource_status']

    response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:102618460408:event_change',
        Message=message
    )
    return response


def lambda_handler(event, context):
    try:
        status_code, message = insert_data(event)
        response = sns(event)
    except Exception as e:
        raise Exception(e)

    return render(200, content=response)


