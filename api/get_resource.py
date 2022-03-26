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
        "body": json.dumps(content) if status_code == 200 else json.dumps({"message": text}) 
    }
    
    
def lambda_handler(event, context):
    params = event['pathParameters']
    resource_name = params['resource_name']
    
    response = []
    
    try:
        data = resource_table.query (
            IndexName='resource-index',
            KeyConditionExpression=Key('resource').eq(resource_name)
        )
        
        response = data['Items']

        if not response:
            return render(500, text='Resouce not found')
        
    except Exception as e:
        raise Exception(e)
        
    return render(200, content=response)

