import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
import httpx
import polyline

load_dotenv()
async def route_functions(data):
    try:
        print('routing_functions called with:', data)
        ors_key = os.getenv('OPEN_ROUTE_SERVICE_TOKEN')
        if not ors_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Open Route Service token is not set."
            )

        s_latitude = data.start_latitude
        s_longitude = data.start_longitude
        e_latitude = data.end_latitude
        e_longitude = data.end_longitude

        # Validate inputs
        if None in (s_latitude, s_longitude, e_latitude, e_longitude):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start and end coordinates must be provided."
            )
        headers = {
            "Authorization": ors_key,
            "Accept": "application/geo+json"
        }

        url = (
            f"https://api.openrouteservice.org/v2/directions/driving-car"
            f"?api_key={ors_key}"
            f"&start={s_longitude},{s_latitude}"
            f"&end={e_longitude},{e_latitude}"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url,headers=headers)

        if response.status_code != 200:
            print(f"ORS error response: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch routing data from Open Route Service."
            )
        
        routing_info = response.json()
        features = routing_info.get("features", [])
        if not features:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid routing response structure: no features found."
            )

        feature = features[0]
        geometry = feature["geometry"]
        summary = feature["properties"]["summary"]

        return {
            "geometry": geometry,
            "distance": summary["distance"],
            "duration": summary["duration"],
        }

    except Exception as e:
        print(f"Error in routing_functions: {e}")
        return None
    

async def reroute_function(data):
    try:
        print('reroute_function called with:', data)

        s_longitude = data.start_longitude
        s_latitude = data.start_latitude
        e_longitude = data.end_longitude
        e_latitude = data.end_latitude

        mapbox_key = os.getenv('mapbox_secret')
        if not mapbox_key: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Mapbox token is not set."
            )

        coordinates = f"{s_longitude},{s_latitude};{e_longitude},{e_latitude}"

        exclusions = []
        for defect in data.defect_nodes:
            exclusions.append(f"point({defect.longitude}%20{defect.latitude})")
        exclusion_query = ",".join(exclusions)

        url = (
            f"https://api.mapbox.com/directions/v5/mapbox/driving/"
            f"{coordinates}?alternatives=true&exclude={exclusion_query}"
            f"&access_token={mapbox_key}"
        )

        print(f"Generated URL: {url}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            print(f"MAPBOX error response: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch routing data from Mapbox."
            )
        
        mapbox_response = response.json()
        rerouting_data = mapbox_to_geojson(mapbox_response)
        if not rerouting_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decode routing data."
            )

        print('Rerouting data:', rerouting_data)
        return rerouting_data

    except Exception as e:
        print(f"Error in reroute_function: {e}")
        return None



def mapbox_to_geojson(mapbox_response):
    if not mapbox_response.get("routes"):
        print("No routes found in Mapbox response.")
        return None
    
    route = mapbox_response["routes"][0]
    if not route:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There's no route returning by mapbox"
            )
    encoded_geometry = route["geometry"]

    try:
        decoded_coords = polyline.decode(encoded_geometry)
    except Exception as e:
        print(f"Failed to decode polyline: {e}")
        return None

    geojson_coords = [[lon, lat] for lat, lon in decoded_coords]

    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": geojson_coords
        },
        "properties": {
            "distance": route.get("distance", 0),
            "duration": route.get("duration", 0)
        }
    }

    return geojson