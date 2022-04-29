import json
import boto3
import urllib.parse
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
zone_table = dynamodb.Table('zone')
boundary_table = dynamodb.Table('boundary')


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


def lambda_handler(event, context):
    params = event['pathParameters']
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    zone_id = params.get('zone_id')

    try:
        boundary_data = boundary_table.get_item(Key={'id': boundary_id})

        if 'Item' in boundary_data:
            boundary_data = boundary_data['Item']
            boundary_name = boundary_data.get('name', '')

            # query through database with a GSI
            data = zone_table.query(
                IndexName='boundary_name-zone_id-index',
                KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
            )

            if not data['Items']:
                return render(404, 'Zone not found')

            for zone in data['Items']:
                zone_table.delete_item(
                    Key={
                        'id': zone['id']
                    }
                )

        else:
            return render(400, 'Boundary not found')

    except Exception as e:
        raise Exception(e)

    return render(200, text='Ok')
