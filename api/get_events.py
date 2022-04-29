import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
event_table = dynamodb.Table('event')
boundary_table = dynamodb.Table('boundary')
zone_table = dynamodb.Table('zone')

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
        zone_id = event['pathParameters'].get('zone_id')
        if boundary.get('Item') is not None:
            boundary_name = boundary['Item'].get('name','')
            if 'zone_id' in event['pathParameters']:
                if zone_id=="":
                    return render(400,text="Must Include zone_id")
                k = Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
            else:
                k = Key('boundary_name').eq(boundary_name)
            data = event_table.query(
                IndexName='boundary_name-zone_id-index',
                KeyConditionExpression=k
            )
            events = sorted(data['Items'],key=lambda event: event['time_created'],reverse=True)
            return render(200,content=events)
        return render(404, text="Boundary Not Found")
    else:
        return render(400, text="Must include a boundary_id")
