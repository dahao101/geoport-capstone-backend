from fastapi import HTTPException, status
from firebase_admin import db
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def save_logs_to_db(data:str):
    try:




        print(f"Attempting to save logs: {data}")
        ref = db.reference("logs") 
        ref.push(data)
        print("Logs saved successfully to the database.")
        return {"message": "Logs saved successfully"}
    
    except Exception as e:
        print("Error in save_logs:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )




