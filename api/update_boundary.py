import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')

allowed_keys = ['name','description','polygon','metadata']

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
    update_names = dict()
    for key, val in body.items():
        if key=="name":
            name_placeholder = "#nm" ##names is a restricted word in dynamo
            update_expression.append(f" {name_placeholder} = :{key},")
            update_values[f":{key}"] = val
            update_names[name_placeholder] = key
        else:
            update_expression.append(f" {key} = :{key},")
            update_values[f":{key}"] = val

    return "".join(update_expression)[:-1], update_values, update_names


def lambda_handler(event, context):
    params = event['pathParameters']
    boundary_id = params['boundary_id']
    body = event['body']
    payload = json.loads(body)
    time = datetime.now()
    try:
        data = boundary_table.query (
            KeyConditionExpression=Key('id').eq(boundary_id)
        )

        if not data['Items']:
            return render(404, text="Not Found")

        d = {}

        for key in payload.keys():
            if key not in allowed_keys:
                message = "Invalid Body, "+key+ " is not allowed"
                return render(400,text=message)
            else:
                d[key] = payload.get(key)

        d['last_modified'] = str(datetime.now())
        a,v,n = get_update_params(d)
        boundary_table.update_item(
            Key={
                'id': data['Items'][0]['id']
            },
            UpdateExpression=a,
            ExpressionAttributeValues=dict(v),
            ExpressionAttributeNames=dict(n)
        )
    except Exception as e:
        raise Exception(e)

    return render(200, text='Ok')
