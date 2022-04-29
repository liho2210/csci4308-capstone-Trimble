import json
import boto3


dynamodb = boto3.resource('dynamodb')
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
        response = boundary_table.get_item(Key={'id': event['pathParameters']['boundary_id']})
        if response.get('Item') is not None:
            return render(200, content=response['Item'])
        else :
            return render(404, text="Not Found")
    else:
        response = boundary_table.scan()
        return render(200,content=response['Items'])
