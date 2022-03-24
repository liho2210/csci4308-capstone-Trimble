import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('zone')

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
    pp = event['pathParameters']
    boundary_id = pp['boundary_id']
    zone_id = pp.get('zone_id')
    
    response = []
    
    try:
        #query through database with a GSI
        if zone_id:
            k = Key('boundary_id').eq(boundary_id) &  Key('zone_id').eq(zone_id)
        else:
            k = Key('boundary_id').eq(boundary_id)
        data = table.query (
            IndexName='boundary-zone-index',
            KeyConditionExpression=k 
        )
        
        for zone in data['Items']:
            d = {
                'zone_id': zone['zone_id'],
                'polygon': json.loads(zone['polygon']), #convert string list to list
                'description': zone['description'],
            }
            response.append(d)
        
    except Exception as e:
        return render(500,'Get zones from boundary Failed.')
    
    return render(200, content=response)
