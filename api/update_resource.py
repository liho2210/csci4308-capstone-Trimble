import json
import boto3
import uuid
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')
zone_table = dynamodb.Table('zone')
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


def check_coords(payload, boundary_name, zone_id):
    message = ''
    new_coords = []
    x = zone_table.query(
        IndexName='boundary_name-zone_id-index',
        KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
    )

    if x['Items']:
        data = x['Items'][0]
        zone_polygon = json.loads(data.get('polygon'))

        for coord in zone_polygon:
            new_coords.append(tuple(coord))

        for point in payload['coordinates']:
            x, y = float(point[0]), float(point[1])
            if not point_inside_polygon(x, y, new_coords):
                message = 'resource coordinates not within zone'

    else:
        message = 'Zone or boundary does not exist'

    return message


def check_zone(new_zone_id, boundary_name):
    message = ''
    zone_data = zone_table.query(
        IndexName='boundary_name-zone_id-index',
        KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(new_zone_id)
    )

    if not zone_data['Items']:
        message = 'new zone_id does not exist'

    return message


def check_boundary(new_boundary_id):
    message = ''
    boundary_data = boundary_table.get_item(Key={'id': new_boundary_id})

    if 'Item' not in boundary_data:
        message = 'Boundary does not exist'

    return message


def check_resource(new_resource_name, boundary_name, zone_id):
    message = ''
    data = resource_table.query(
        IndexName='boundary_name-zone_id-index',
        KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
    )

    for r in data['Items']:
        if r['resource_name'] == new_resource_name:
            message = 'New resource name already exist in this boundary'

    return message


def update_data(data, payload):
    try:
        d = {
            'boundary_name': str(payload.get('new_boundary_id', data['boundary_name'])),
            'zone_id': str(payload.get('new_zone_id', data['zone_id'])),
            'resource_name': str(payload.get('new_resource_name', data['resource_name'])),
            'resource_type': str(payload.get('resource_type', data['resource_type'])),
            'resource_status': str(payload.get('resource_status', data['resource_status'])),
            'description': payload.get('description', data['description']),
            'coordinates': str(payload.get('coordinates', data['coordinates'])),
            'amount': str(payload.get('amount', data['amount'])),
            'last_modified': str(datetime.now()),
            'metadata': payload.get('metadata', {})
        }
        a, v = get_update_params(d)

        resource_table.update_item(
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
    params = event['pathParameters']
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    zone_id = params['zone_id']
    resource = params['resource_name']
    message = ''
    text = ''
    zone_data = []

    boundary_data = boundary_table.get_item(Key={'id': boundary_id})

    if 'Item' in boundary_data:
        boundary_data = boundary_data['Item']
        boundary_name = boundary_data.get('name', '')
    else:
        return render(400, 'Boundary does not exist')

    new_coordinates = payload.get('coordinates', '')
    if new_coordinates:
        text += check_coords(payload, boundary_name, zone_id)

    new_zone_id = payload.get('new_zone_id', '')
    if new_zone_id:
        message = check_zone(new_zone_id, boundary_name)
        text += ', ' + message if text else message

    new_boundary_id = payload.get('new_boundary_id', '')
    if new_boundary_id:
        message = check_boundary(new_boundary_id)
        text += ', ' + message if text else message

    new_resource_name = payload.get('new_resource_name', '')
    if new_resource_name:
        message = check_resource(new_resource_name, boundary_name, zone_id)
        text += ', ' + message if text else message

    if text:
        return render(412, text=text)

    try:
        data = resource_table.query(
            IndexName='resource_name-zone_id-index',
            KeyConditionExpression=Key('resource_name').eq(resource) & Key('zone_id').eq(zone_id)
        )

        for z in data['Items']:
            if z['boundary_name'] == str(boundary_name):
                zone_data = z
                break

        if zone_data:
            update_data(zone_data, payload)
            return render(200, 'OK')
        else:
            return render(409, text='Resource does not exist')

    except Exception as e:
        raise Exception(e)

    return render(status_code, text=text)
