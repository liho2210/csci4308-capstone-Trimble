import json
import boto3


dynamodb = boto3.resource('dynamodb')
event_table = dynamodb.Table('event')

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
        response = event_table.get_item(Key={'boundary_id': event['pathParameters']['boundary_id']})
        if response.get('Item') is not None:
            return render(200, content=response['Item'])
        else :
            return render(404, text="Not Found")
    else:
        return render(400, text="Must include a boundary_id")
