from fastapi import HTTPException, status
from firebase_admin import auth, db
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def fetch_logs():
    try:
        ref = db.reference("logs")
        logs_dict = ref.get()  
        logs_list = list(logs_dict.values()) if isinstance(logs_dict, dict) else logs_dict
        return logs_list
     
    except Exception as e:
        print("Error in fetch_logs:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Correct the function call inside your route handler
async def get_logs():
    return await fetch_logs()  # Call fetch_logs properly
