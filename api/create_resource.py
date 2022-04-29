import json
import boto3
import uuid
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
boundary_table = dynamodb.Table('boundary')
resource_table = dynamodb.Table('resource')
zone_table = dynamodb.Table('zone')
client = boto3.client('lambda')


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
            IndexName='boundary_name-zone_id-index',
            KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
        )
        if x['Items']:
            zone_data = x['Items'][0]
            zone_polygon = json.loads(zone_data.get('polygon'))

            for coord in zone_polygon:
                zone_coords.append(tuple(coord))

            for point in payload['coordinates']:
                x, y = float(point[1]), float(point[0])
                if not point_inside_polygon(y, x, zone_coords):
                    return (400, 'Location of resource is not within boundary and zone')

            resource_table.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'zone_id': zone_id,
                    'boundary_name': boundary_name,
                    'coordinates': str(payload['coordinates']),
                    'resource_name': payload.get('resource_name', ''),
                    'resource_type': payload.get('resource_type', ''),
                    'resource_status': payload.get('resource_status', ''),
                    'amount': payload.get('amount', ''),
                    'description': payload.get('description', ''),
                    'time_created': str(datetime.now()),
                    'last_modified': str(datetime.now()),
                    'metadata': payload.get('metadata', {})
                }
            )
        else:
            return (400, 'Zone or Boundary does not exist.')

    except Exception as e:
        raise Exception(e)

    return (200, 'OK')


def lambda_handler(event, context):
    params = event['pathParameters']
    boundary_id = urllib.parse.unquote_plus(params['boundary_id'])
    zone_id = params.get('zone_id')
    body = event['body']
    payload = json.loads(body)
    resource = payload.get('resource_name')
    text = ''
    resource_data = []

    try:
        boundary_data = boundary_table.get_item(Key={'id': boundary_id})

        if 'Item' in boundary_data:
            boundary_data = boundary_data['Item']
            boundary_name = boundary_data.get('name', '')
        else:
            return render(400, 'Boundary does not exist')

        data = resource_table.query(
            IndexName='boundary_name-zone_id-index',
            KeyConditionExpression=Key('boundary_name').eq(boundary_name) & Key('zone_id').eq(zone_id)
        )

        for r in data['Items']:
            if r['resource_name'] == str(resource):
                resource_data = r
                break

        if resource_data:
            return render(409, text='Resource is already created under zone_id and boundary_id')
        else:
            status_code, message = insert_data(boundary_name, zone_id, payload)
            path_data = {'boundary_name': boundary_name, 'zone_id': zone_id}
            event_data = {**payload, **path_data}
            response = client.invoke(
                FunctionName='arn:aws:lambda:us-east-1:102618460408:function:create_event',
                InvocationType='RequestResponse',
                Payload=json.dumps(event_data)
            )


    except Exception as e:
        raise Exception(e)

    return render(status_code, message)
