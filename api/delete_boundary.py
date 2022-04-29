import json
import boto3
from boto3.dynamodb.conditions import Key

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
    params = event['pathParameters']
    boundary_id = params['boundary_id']

    try:
        data = boundary_table.query (
            KeyConditionExpression=Key('id').eq(boundary_id)
        )

        if not data['Items']:
            return render(404, text="Not Found")

        for item in data['Items']:
            boundary_table.delete_item(
                Key={
                    'id': item['id']
                }
            )

    except Exception as e:
        raise Exception(e)

    return render(200, text='Ok')
