import json
import boto3


dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

def lambda_handler(event, context):
    item = boundary_table.get_item(Key={'id': event['pathParameters']['boundary_id']})
    if item != None:
        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps(item),
            'isBase64Encoded': False

        }
    else :
        return {
            'statusCode': 404,
            'body': json.dumps('Not Found')
        }
