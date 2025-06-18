from fastapi import HTTPException, status
import httpx
from dotenv import load_dotenv
import os
load_dotenv()
async def reverse_location(data):
    try:
        print('reverse_location called with:',data)
        latitude = data.latitude
        longitude = data.longitude
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude and longitude must be provided."
            )
        api_key = os.getenv("LOCATION_IQ_TOKEN")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key for LocationIQ is not set in environment variables."
            )
        
        async with httpx.AsyncClient() as client:
            url = (
                f"https://us1.locationiq.com/v1/reverse?"
                f"key={api_key}&lat={latitude}&lon={longitude}&format=json"
            )
            response = await client.get(url)
            if response.status_code == 200:
                location_info = response.json() if hasattr(response, "json") else await response.json()
                village = location_info.get("address", {}).get("village")
                
                if not village:
                    village = location_info.get("address", {}).get("suburb") or \
                              location_info.get("address", {}).get("hamlet") or \
                              location_info.get("address", {}).get("county")
                
                return village
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error fetching location data: {response.text}"
                )

            

    except Exception as e:
        print(f"Error in reverse_location: {e}")
        return None