import json
import boto3
import urllib.parse
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('zone')
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
    zone_id = params.get('zone_id')
    response = []

    try:
        boundary_data = boundary_table.get_item(Key={'id': boundary_id})

        if 'Item' in boundary_data:
            boundary_data = boundary_data['Item']
            boundary_name = boundary_data.get('name', '')

            # query through database with a GSI
            if zone_id:
                k = Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
            else:
                k = Key('boundary_name').eq(boundary_name)
            data = table.query(
                IndexName='boundary_name-zone_id-index',
                KeyConditionExpression=k
            )

            for zone in data['Items']:
                d = {
                    'zone_id': zone['zone_id'],
                    'polygon': json.loads(zone['polygon']),  # convert string list to list
                    'description': zone['description'],
                    'metadata': zone.get('metadata', {})
                }
                response.append(d)

            if not response:
                return render(500, text='Get zones from boundary Failed.')
        else:
            return render(400, 'Boundary does not exist')

    except Exception as e:
        raise Exception(e)

    return render(200, content=response)
