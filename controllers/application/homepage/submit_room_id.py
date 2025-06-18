from fastapi import HTTPException, status,Header, BackgroundTasks
from firebase_admin import auth,db
from backend.services.FirebaseServices import initialize_firebase

async def submit_id(id:str,room_id:str):
    try:
        ref = db.reference(f'generated_room_id/{id}')
        ref.set(room_id)  
        return {"status": "success", "id": id, "data": room_id}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}