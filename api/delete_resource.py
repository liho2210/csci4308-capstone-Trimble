import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
resource_table = dynamodb.Table('resource')

def render(status_code, text=None, content=None):
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": None if status_code == 204 else json.dumps({"message": text}) 
    }
    
def lambda_handler(event, context):
    params = event['pathParameters']
    resource_name = params['resource_name']
    
    try:
        #query through database with a GSI
        data = resource_table.query (
            IndexName='resource-index',
            KeyConditionExpression=Key('resource').eq(resource_name)
        )
        
        if not data['Items']:
            return render(204)
        
        #delete item from DB through primary key
        for item in data['Items']:
            resource_table.delete_item(
                Key={
                    'id': item['id']
                }
            )
        
    except Exception as e:
        raise Exception(e)
    
    return render(200, text='Ok')
