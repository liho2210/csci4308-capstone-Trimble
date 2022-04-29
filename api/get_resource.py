import json
import boto3
import urllib.parse
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
resource_table = dynamodb.Table('resource')
boundary_table = dynamodb.Table('boundary')


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
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    resource_name = params.get('resource_name')
    zone_id = params.get('zone_id')

    response = []

    try:
        boundary_data = boundary_table.get_item(Key={'id': boundary_id})

        if 'Item' in boundary_data:
            boundary_data = boundary_data['Item']
            boundary_name = boundary_data.get('name', '')
        else:
            return render(400, 'Boundary does not exist')

        if resource_name:
            data = resource_table.query(
                IndexName='resource_name-zone_id-index',
                KeyConditionExpression=Key('resource_name').eq(resource_name) & Key('zone_id').eq(zone_id)
            )

            for resource in data['Items']:
                if resource['boundary_name'] == str(boundary_name):
                    response = resource
                    break

        else:
            data = resource_table.query(
                IndexName='boundary_name-zone_id-index',
                KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
            )
            for r in data['Items']:
                response.append(r)

        if not response:
            return render(500, text='No resource found')

    except Exception as e:
        raise Exception(e)

    return render(200, content=response)

