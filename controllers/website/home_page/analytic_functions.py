from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from fastapi.responses import JSONResponse
from collections import defaultdict
from backend.services.FirebaseServices import  initialize_firebase
import asyncio
from backend.module_functions.filter_report_by_barangay import filterReportsByBarangay

initialize_firebase()



async def rank_each_highest_barangay():
    try:
        ref = db.reference('reports')
        reports = ref.get()
        if not reports:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports found in the collection"
            )
        
        analytics_data = [
            {   
                "type": report_data.get('TypeOfReport', 'N/A'),
                "status": report_data.get('status', 'Unknown'),
                "latitude": report_data.get('location', {}).get('latitude', None),
                "longitude": report_data.get('location', {}).get('longitude', None),
            }
            for report_id, report_data in reports.items()
            if report_data.get('status') != "False Report"
        ]

        reports_with_village = await filterReportsByBarangay(analytics_data)
        area_count_map = defaultdict(lambda: {"Vehicle Collision": 0, "Road Defect": 0})

        allowed_types = {
            "vehicle collision": "Vehicle Collision",
            "road defects": "Road Defect"
        }

        for report in reports_with_village:
            village = report.get("village") or "Unknown"
            report_type = report.get("type", "").lower()

            if report_type in allowed_types:
                key = allowed_types[report_type]
                area_count_map[village][key] += 1

        sorted_areas = sorted(
            area_count_map.items(),
            key=lambda x: x[1]["Vehicle Collision"] + x[1]["Road Defect"],
            reverse=True
        )[:5]

        formatted_result = [
            {"village": village, "typeCounts": counts} for village, counts in sorted_areas
        ]

        return formatted_result
   
    
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching reports: {str(e)}"
        )
