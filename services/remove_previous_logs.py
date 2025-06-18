from fastapi import HTTPException, status
from firebase_admin import db
from backend.services.FirebaseServices import initialize_firebase
from datetime import datetime, timedelta

initialize_firebase()

async def remove_previous_logs():
    try:
        print("Attempting to remove previous logs.")
        ref = db.reference("logs")
        logs_list = ref.get()

        if not logs_list:
            print("No logs found.")
            return False

        cutoff_time = datetime.now() - timedelta(days=1)

        for log_id, log_data in logs_list.items():
            log_date_str = log_data.get("date")

            if log_date_str:
                try:
                    log_date = datetime.strptime(log_date_str, "%Y-%m-%dT%H:%M:%S")
                    
                    if log_date < cutoff_time:
                        db.reference(f"logs/{log_id}").delete()
                        print(f"Deleted log {log_id} with date {log_date_str}.")
                
                except ValueError:
                    print(f"Skipping log {log_id}, invalid date format: {log_date_str}")

        print("Old logs deleted successfully.")
        return True

    except Exception as e:
        print("Error in remove_previous_logs:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

def current_date():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
