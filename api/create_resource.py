import json
import boto3
import uuid
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('boundary')
resource_table = dynamodb.Table('resource')
zone_table = dynamodb.Table('zone')


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


def point_inside_polygon(x, y, poly, include_edges=True):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if p1y == p2y:
            if y == p1y:
                if min(p1x, p2x) <= x <= max(p1x, p2x):
                    # point is on horizontal edge
                    inside = include_edges
                    break
                elif x < min(p1x, p2x):  # point is to the left from current edge
                    inside = not inside
        else:  # p1y!= p2y
            if min(p1y, p2y) <= y <= max(p1y, p2y):
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x

                if x == xinters:  # point is right on the edge
                    inside = include_edges
                    break

                if x < xinters:  # point is to the left from current edge
                    inside = not inside

        p1x, p1y = p2x, p2y

    return inside


def insert_data(boundary_name, zone_id, payload):
    zone_coords = []
    try:
        x = zone_table.query(
            IndexName='boundary-zone-index',
            KeyConditionExpression=Key('boundary_id').eq(boundary_name) & Key('zone_id').eq(zone_id)
        )
        if x['Items']:
            zone_data = x['Items'][0]
            zone_polygon = json.loads(zone_data.get('polygon'))

            for coord in zone_polygon:
                zone_coords.append(tuple(coord))

            x, y = float(payload['coordinates'][0]), float(payload['coordinates'][1])
            if not point_inside_polygon(x, y, zone_coords):
                return (400, 'Location of resource is not within boundary and zone')

            resource_table.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'zone_id': zone_id,
                    'boundary_id': boundary_name,
                    'coordinates': str(payload['coordinates']),
                    'resource_name': payload['resource_name'],
                    'resource_type': payload['resource_type'],
                    'resource_status': payload['resource_status'],
                    'amount': payload['amount'],
                    'description': payload.get('description', ''),
                    'time_created': str(datetime.now()),
                    'last_modified': str(datetime.now())
                }
            )
        else:
            (400, 'Zone or Boundary does not exist.')

    except Exception as e:
        raise Exception(e)


def lambda_handler(event, context):
    params = event['pathParameters']
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    zone_id = params.get('zone_id')
    body = event['body']
    payload = json.loads(body)
    resource = payload.get('resource_name')
    text = ''
    zone_data = []

    try:
        data = resource_table.query(
            IndexName='resource_name-zone_id-index',
            KeyConditionExpression=Key('resource_name').eq(resource) & Key('zone_id').eq(zone_id)
        )

        for zones in data['Items']:
            if zones['boundary_id'] == str(boundary_id):
                zone_data = zones
                break

        if zone_data:
            return render(409, text='Resource is already created under zone_id and boundary_id')
        else:
            insert_data(boundary_id, zone_id, payload)
            return render(200, text='OK')

    except Exception as e:
        raise Exception(e)

    return render(status_code, text=text)
