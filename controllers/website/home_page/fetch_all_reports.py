from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from backend.services.FirebaseServices import  initialize_firebase
import asyncio

initialize_firebase()

active_connections = {}

async def fetch_all_reports():
    try:
        ref = db.reference('reports')
        total_reports = ref.get()

        if not total_reports:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reports found in the collection"
            )

        unsolved_reports_data = [
            {
                "report_id": report_id,
                "type": report_data.get('TypeOfReport', 'N/A'),
                "status": report_data.get('status', 'Unknown'),
                "reference": report_data.get('reference', 'N/A'),
                "reporter": report_data.get('reporter', 'Unknown'),
                "image": report_data.get('image', ''),
                "severity": report_data.get('Severity', False),
                "date_reported": report_data.get('DateAndTime', 'Unknown'),
                "location": report_data.get('location', {}),
                "passable": report_data.get('passable', False),
                "latitude": report_data.get('location', {}).get('latitude', None),
                "longitude": report_data.get('location', {}).get('longitude', None),
                "version":report_data.get('version',1)
            }
            for report_id, report_data in total_reports.items()
            if isinstance(report_data, dict) and report_data.get('status') != 'Solved'
        ]

        return unsolved_reports_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )

async def websocket_listener(websocket: WebSocket):
    await websocket.accept()
    active_connections[websocket] = True

    try:
        reports = await fetch_all_reports()
        await websocket.send_json(reports)

        def firebase_listener(event):
            updated_report = event.data  
            print(f"Report updated: {updated_report}")

            for connection in active_connections:
                asyncio.create_task(connection.send_json(updated_report))

        ref = db.reference('reports')
        ref.listen(firebase_listener) 

        while True:
            await websocket.receive_text() 

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        del active_connections[websocket]

    except Exception as e:
        print(f"Error in WebSocket listener: {e}")
        await websocket.send_json({"error": "An error occurred while processing the request"})
        del active_connections[websocket]
