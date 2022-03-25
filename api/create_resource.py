import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('boundary')
resource_table = dynamodb.Table('resource')


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


def get_update_params(body):

    update_expression = ["set "]
    update_values = dict()

    for key, val in body.items():
        update_expression.append(f" {key} = :{key},")
        update_values[f":{key}"] = val

    return "".join(update_expression)[:-1], update_values


def update_data(data, payload):
    # print(data)
    try:
        
        d = {
            'zone_id': payload.get('zone_id', data['zone_id']),
            'boundary_id': payload.get('boundary_id', data['boundary_id']),
            'resource_status': payload.get('resource_status', data['resource_status']),
            'amount': payload.get('amount', data['amount']),
            
        }
        a,v = get_update_params(d)
        
        resource_table.update_item(
            Key={
                'id': data['id']
            },
            UpdateExpression=a,
            ExpressionAttributeValues=dict(v)
        )
        
    except Exception as e:
        raise Exception(e)


def insert_data(payload):
    
    try:
        resource_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'zone_id': payload['zone_id'],
                'boundary_id': payload['boundary_id'],
                'description': payload.get('description', ''),
                'resource': payload['resource'],
                'resource_type': payload['resource_type'],
                'resource_status': payload['resource_status'],
                'amount': payload['amount']
            }
        )
    
    except Exception as e:
        raise Exception(e)
    
def lambda_handler(event, context):

    body = event['body']
    payload = json.loads(body)
    resource = payload.get('resource')
    
    try:
        data = resource_table.query (
            IndexName='resource-index',
            KeyConditionExpression=Key('resource').eq(resource)
        )
        # print(data)
        
        if data['Items']:
            update_data(data=data['Items'][0], payload=payload)
        else:
            insert_data(payload)
        
    except Exception as e:
        raise Exception(e)
    
    return render(200, text='OK')
