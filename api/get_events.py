import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
event_table = dynamodb.Table('event')
boundary_table = dynamodb.Table('boundary')

def render(status_code, text=None, content=None):
    if status_code==200:
        body = json.dumps(content)
    else:
        body = json.dumps({"message": text})
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": body
    }

def lambda_handler(event, context):
    if event['pathParameters'] is not None:
        boundary = boundary_table.get_item(Key={'id': event['pathParameters']['boundary_id']})
        if boundary.get('Item') is not None:
            boundary_name = boundary['Item'].get('name','')
            k = Key('boundary_name').eq(boundary_name)
            data = event_table.query(
                IndexName='boundary_name-index',
                KeyConditionExpression=k
            )
            events = sorted(data['Items'],key=lambda event: event['time_created'],reverse=True)
            return render(200,content=events)
        return render(404, text="Boundary Not Found")
    else:
        return render(400, text="Must include a boundary_id")
