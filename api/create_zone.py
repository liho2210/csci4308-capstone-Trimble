import json
import boto3
import uuid

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


def lambda_handler(event, context):
    boundary_id = "CU Campus-2022-03-23 03:16:40.143632"
    new_coords = []
    body = event['body']
    payload = json.loads(body)

    try:
        x = table.get_item(Key={'id': boundary_id})

        if 'Item' not in x:
            return render(400, message='Boundary does not exist.')
            
        boundary_polygon = x['Item'].get('polygon')

        for coord in boundary_polygon:
            new_coords.append(tuple(json.loads(coord)))
        
        for point in payload['polygon']:
            x,y = float(point[0]), float(point[1])
            if not point_inside_polygon(x,y, new_coords):
                return render(400, message='Zone not in Boundary')
        
        zone_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'name': payload['zone_id'],
                'description': 'Farrand Field',
                'polygon': str(payload['polygon']),
                'boundary_id': boundary_id
            }
        )
        
    except Exception as e:
        raise Exception(e)
    
    return render(200, text='OK')
