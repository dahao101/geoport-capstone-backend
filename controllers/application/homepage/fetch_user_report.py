from fastapi import HTTPException
from firebase_admin import db

async def FetchUserReported(id: str):
    print('fetching user reports')

    ref = db.reference('/reports')
    reports = ref.get()

    if not reports:
        return {
            "success": False,
            "message": "No reports retrieved",
            "data": {}
        }

    user_reports = {
    key: report
    for key, report in reports.items()
    if isinstance(report, dict) and report.get('reference') == id
}


    return {
        "success": True,
        "message": "Reports retrieved successfully",
        "data": user_reports
    }
