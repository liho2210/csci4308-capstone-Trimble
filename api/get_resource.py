import json
import boto3
import urllib.parse
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
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    resource_name = params.get('resource_name')
    zone_id = params.get('zone_id')

    response = []

    try:
        if resource_name:
            data = resource_table.query(
                IndexName='resource_name-zone_id-index',
                KeyConditionExpression=Key('resource_name').eq(resource_name) & Key('zone_id').eq(zone_id)
            )

            for resource in data['Items']:
                if resource['boundary_id'] == str(boundary_id):
                    response = resource
                    break

        else:
            data = resource_table.query(
                IndexName='boundary_id-zone_id-index',
                KeyConditionExpression=Key('boundary_id').eq(boundary_id) & Key('zone_id').eq(zone_id)
            )
            for r in data['Items']:
                d = {
                    'resource_name': r['resource_name'],
                    'resource_type': r['resource_type'],
                    'resource_status': r['resource_status'],
                    'amount': r['amount'],
                    'coordinates': json.loads(r['coordinates']),  # convert string list to list
                    'description': r['description'],
                }
                response.append(d)

        if not response:
            return render(500, text='No resource found')

    except Exception as e:
        raise Exception(e)

    return render(200, content=response)

