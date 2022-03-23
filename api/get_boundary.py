import json
import boto3


dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

def lambda_handler(event, context):
    response = boundary_table.get_item(Key={'id': event['pathParameters']['boundary_id']})
    if response.get('Item') is not None:
        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps(response['Item']),
            'isBase64Encoded': False

        }
    else :
        return {
            'statusCode': 404,
            'headers': {},
            'body': json.dumps('Not Found'),
            'isBase64Encoded': False
        }
