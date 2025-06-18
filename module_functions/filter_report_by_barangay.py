from fastapi import FastAPI, Query
import httpx
import os
from dotenv import load_dotenv
from collections import Counter


load_dotenv()
async def filterReportsByBarangay(reports:list):
    try:
        print('processing data')
        api_key = os.getenv('LOCATION_IQ_TOKEN')
        if not api_key:
             print("No API key found for LocationIQ")
             return {"error": "Missing LocationIQ API key"}
        
        enriched_data = []
        
        async with httpx.AsyncClient() as client:
            for data in reports:
                lat = data.get("latitude")
                lon = data.get("longitude")

                if lat is None or lon is None:
                    data["village"] = None
                    enriched_data.append(data)
                    continue


                url = (
                    f"https://us1.locationiq.com/v1/reverse?"
                    f"key={api_key}&lat={lat}&lon={lon}&format=json"
                )

                response = await client.get(url)
                if response.status_code == 200:
                    location_info = response.json()
                    village = location_info.get("address", {}).get("village")

                    if not village:
                        village = location_info.get("address", {}).get("suburb") or \
                                  location_info.get("address", {}).get("hamlet") or \
                                  location_info.get("address", {}).get("county")

                    data["village"] = village
                else:
                    data["village"] = None
                enriched_data.append(data)
        village_names = [entry['village'] for entry in enriched_data if entry['village']]
        village_counts = Counter(village_names)
        formatted_data = [{"village": name, "count": count} for name, count in village_counts.most_common(5)]
        return enriched_data
        
    except Exception as e:
        print(f'Something went wrong: {e}')
        return {"error": str(e)}
