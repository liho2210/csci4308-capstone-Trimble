import json
import boto3
import uuid
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('boundary')
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


def insert_data(boundary_name, payload):
    new_coords = []
    try:
        x = table.query(
            IndexName='boundary-name-index',
            KeyConditionExpression=Key('name').eq(boundary_name)
        )

        if x['Items']:
            boundary_data = x['Items'][0]
            boundary_polygon = json.loads(boundary_data.get('polygon'))

            for coord in boundary_polygon:
                new_coords.append(tuple(coord))

            for point in payload['polygon']:
                x, y = float(point[0]), float(point[1])
                if not point_inside_polygon(x, y, new_coords):
                    return (400, 'Zone coordinates not within Boundary')

            zone_table.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'zone_id': payload['zone_id'],
                    'description': payload.get('description', ''),
                    'polygon': str(payload['polygon']),
                    'boundary_id': boundary_name,
                    'time_created': str(datetime.now()),
                    'last_modified': str(datetime.now())
                }
            )
            return (200, "OK")
        else:
            return (400, 'Boundary does not exist.')

    except Exception as e:
        raise Exception(e)


def lambda_handler(event, context):
    body = event['body']
    payload = json.loads(body)
    params = event['pathParameters']
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    zone_id = payload.get('zone_id')

    try:
        data = zone_table.query(
            IndexName='boundary-zone-index',
            KeyConditionExpression=Key('boundary_id').eq(boundary_id) & Key('zone_id').eq(zone_id)
        )

        if data['Items']:
            status_code, text = 409, 'Zone already exist'
        else:
            status_code, text = insert_data(boundary_id, payload)

    except Exception as e:
        raise Exception(e)

    return render(status_code, text=text)
