from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from backend.services.FirebaseServices import  initialize_firebase
from backend.module_functions.extract_report_data import extract_report
import asyncio

initialize_firebase()

# This function will group the data by report status
def filterStatus():
    try:
        print('processing data')
        ref = db.reference('reports')
        total_reports = ref.get()

        if not total_reports:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reports found in the collection"
            )

        pending_reports = [
            extract_report(report_id, report_data)
            for report_id, report_data in total_reports.items()
            if isinstance(report_data, dict) and report_data.get('status') not in ['Solved', 'False Report']
        ]

        solved_reports = [
            extract_report(report_id, report_data)
            for report_id, report_data in total_reports.items()
            if isinstance(report_data, dict) and report_data.get('status') != 'Pending' and report_data.get('status') != 'False Report'
        ]   

        false_reports = [
            extract_report(report_id, report_data)
            for report_id, report_data in total_reports.items()
            if isinstance(report_data, dict) and report_data.get('status') != 'Solved' and report_data.get('status') != 'Pending'
        ]
        return {
                "pending": pending_reports,
                "solved": solved_reports,
                "false": false_reports
            }

    except Exception as e:
        print(f"Error filtering reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while filtering reports"
        )
