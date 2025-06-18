from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from backend.services.FirebaseServices import  initialize_firebase
import asyncio

initialize_firebase()



async def get_analytics_data():
    try:
        ref = db.reference('reports')
        total_reports = ref.get()

        if not total_reports:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reports found in the collection"
            )

        analytics_data = [
            {
                "report_id": report_id,
                "type": report_data.get('TypeOfReport', 'N/A'),
                "status": report_data.get('status', 'Unknown'),
                "reference": report_data.get('reference', 'N/A'),
                "reporter": report_data.get('reporter', 'Unknown'),
                "image": report_data.get('image', ''),
                "severity": report_data.get('Severity', False),
                "date_reported": report_data.get('DateAndTime', 'Unknown'),
                "passable": report_data.get('passable', False),
                "latitude": report_data.get('location', {}).get('latitude', None),
                "longitude": report_data.get('location', {}).get('longitude', None),
                "version":report_data.get('version',1)
            }
            for report_id, report_data in total_reports.items()
        ]
        
        return analytics_data

    except Exception as e:
 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )

