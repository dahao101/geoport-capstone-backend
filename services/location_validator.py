import requests
from shapely.geometry import Point, LineString


def get_node_coordinates(node_id):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node({node_id});
    out body;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    if data['elements']:
        node = data['elements'][0]
        lat = node['lat']
        lon = node['lon']
        return lat, lon
    return None, None

def get_osm_roads_near_location(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way(around:50,{lat},{lon})[highway];
    out body;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    return data

def is_location_on_road(lat, lon, osm_data):
    point = Point(lon, lat)  

    for element in osm_data['elements']:
        if element['type'] == 'way':
            road_points = []
            for node_id in element['nodes']:
                road_lat, road_lon = get_node_coordinates(node_id)
                if road_lat and road_lon:
                    road_points.append((road_lon, road_lat))
            
            road_line = LineString(road_points)  

            if road_line.distance(point) < 10:  
                return True, element  

    return False, None  

def generate_report(lat, lon):
    osm_data = get_osm_roads_near_location(lat, lon)
    is_on_road, road_info = is_location_on_road(lat, lon, osm_data)
    print('location validator is running')
    if is_on_road:
        road_name = road_info['tags'].get('name', 'Unknown road')
        road_type = road_info['tags'].get('highway', 'N/A')
        print(f"Location is on a road: {road_info['tags'].get('name', 'Unknown road')} (Type: {road_info['tags'].get('highway', 'N/A')})")
        return {"status": True,"message": f"Location is on a road: {road_name} (Type: {road_type})"
        }
    else:
        return {"status": False,"message": "Location is not on a road."}
