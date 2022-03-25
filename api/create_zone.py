import json
import boto3
import uuid
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


def update_data(data, payload):
    new_coords = []
    boundary_id = payload['boundary_id']
    try:
        x = table.get_item(Key={'id': boundary_id})

        if 'Item' not in x:
            return render(400, text='Boundary does not exist.')
            
        boundary_polygon = x['Item'].get('polygon')
        
        for coord in boundary_polygon:
            new_coords.append(tuple(json.loads(coord)))
        
        for point in payload['polygon']:
            x,y = float(point[0]), float(point[1])
            if not point_inside_polygon(x,y, new_coords):
                return render(400, text='Zone not in Boundary')
        
        d = {
            'description': payload.get('description', ''),
            'polygon': str(payload['polygon']),
        }
        a,v = get_update_params(d)
        
        zone_table.update_item(
            Key={
                'id': data['id']
            },
            UpdateExpression=a,
            ExpressionAttributeValues=dict(v)
        )
        
    except Exception as e:
        raise Exception(e)

def insert_data(payload):
    new_coords = []
    boundary_id = payload['boundary_id']
    try:
        x = table.get_item(Key={'id': boundary_id})

        if 'Item' not in x:
            return render(400, text='Boundary does not exist.')
            
        boundary_polygon = x['Item'].get('polygon')
        
        for coord in boundary_polygon:
            new_coords.append(tuple(json.loads(coord)))
        
        for point in payload['polygon']:
            x,y = float(point[0]), float(point[1])
            if not point_inside_polygon(x,y, new_coords):
                return render(400, text='Zone not in Boundary')
        
        zone_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'zone_id': payload['zone_id'],
                'description': payload.get('description', ''),
                'polygon': str(payload['polygon']),
                'boundary_id': payload['boundary_id']
            }
        )
        
    except Exception as e:
        raise Exception(e)
    
def lambda_handler(event, context):
    body = event['body']
    payload = json.loads(body)
    boundary_id = payload.get('boundary_id')
    zone_id = payload.get('zone_id')
    
    try:
        data = zone_table.query (
            IndexName='boundary-zone-index',
            KeyConditionExpression=Key('boundary_id').eq(boundary_id) &  Key('zone_id').eq(zone_id)
        )
        print(data)
        if data['Items']:
            update_data(data=data['Items'][0], payload=payload)
        else:
            insert_data(payload)

    except Exception as e:
        raise Exception(e)
    
    return render(200, text='OK')
