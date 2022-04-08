import json
import boto3
import uuid
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


def get_update_params(body):
    update_expression = ["set "]
    update_values = dict()

    for key, val in body.items():
        update_expression.append(f" {key} = :{key},")
        update_values[f":{key}"] = val

    return "".join(update_expression)[:-1], update_values


def check_polygon(polygon, boundary_name):
    message = ''
    new_coords = []
    x = table.query(
        IndexName='boundary-name-index',
        KeyConditionExpression=Key('name').eq(boundary_name)
    )

    if x['Items']:
        boundary_data = x['Items'][0]
        boundary_polygon = json.loads(boundary_data.get('polygon'))

        for coord in boundary_polygon:
            new_coords.append(tuple(coord))

        for point in polygon:
            x, y = float(point[0]), float(point[1])
            if not point_inside_polygon(x, y, new_coords):
                message = 'Zone coordinates not within Boundary'
                break
    else:
        message = 'Boundary does not exist'

    return message


def check_zone(new_zone_id, boundary_name):
    message = ''
    zone_data = zone_table.query(
        IndexName='boundary-zone-index',
        KeyConditionExpression=Key('boundary_id').eq(boundary_name)
    )

    for zone in zone_data['Items']:
        if new_zone_id == zone['zone_id']:
            message = 'zone_id already exist'
            break

    return message


def check_boundary(new_boundary_name):
    message = ''
    boundary_data = table.query(
        IndexName='boundary-name-index',
        KeyConditionExpression=Key('boundary_id').eq(new_boundary_name)
    )

    if not boundary_data['Items']:
        message = 'New Boundary Name does not exist'

    return message


def update_data(data, payload):
    try:
        d = {
            'boundary_id': str(payload.get('new_boundary_id', data['boundary_id'])),
            'zone_id': str(payload.get('new_zone_id', data['zone_id'])),
            'description': payload.get('description', data['description']),
            'polygon': str(payload.get('polygon', data['polygon'])),
            'last_modified': str(datetime.now())
        }
        a, v = get_update_params(d)

        zone_table.update_item(
            Key={
                'id': data['id']
            },
            UpdateExpression=a,
            ExpressionAttributeValues=dict(v)
        )
        return (200, "OK")

    except Exception as e:
        raise Exception(e)


def lambda_handler(event, context):
    body = event['body']
    payload = json.loads(body)
    boundary_id = payload.get('boundary_id')
    zone_id = payload.get('zone_id')
    message = ''
    text = ''

    new_polygon = payload.get('polygon', '')
    if new_polygon:
        text += check_polygon(new_polygon, boundary_name=payload['boundary_id'])

    new_zone_id = payload.get('new_zone_id', '')
    if new_zone_id:
        message = check_zone(new_zone_id, boundary_id)
        text += ', ' + message if text else message

    new_boundary_id = payload.get('new_boundary_id', '')
    if new_boundary_id:
        message = check_boundary(new_boundary_id)
        text += ', ' + message if text else message

    if text:
        return render(412, text=text)

    try:
        data = zone_table.query(
            IndexName='boundary-zone-index',
            KeyConditionExpression=Key('boundary_id').eq(boundary_id) & Key('zone_id').eq(zone_id)
        )

        if data['Items']:
            status_code, text = update_data(data=data['Items'][0], payload=payload)

        else:
            status_code, text = 400, 'Zone does not exist'

    except Exception as e:
        raise Exception(e)

    return render(status_code, text=text)
