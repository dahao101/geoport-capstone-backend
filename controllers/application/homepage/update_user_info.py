from fastapi import HTTPException, status,Header, BackgroundTasks
from firebase_admin import auth,db
from backend.services.FirebaseServices import initialize_firebase


initialize_firebase()

async def update_user_profile(id: str, new_name: str, new_profile: str):
  
    try:
        ref = db.reference(f'/users/{id}')

        ref.update({
            'name': new_name,
            'image': new_profile
        })
        print(f"User profile updated: {new_name}, {new_profile}")
        return {"status": "success", "message": "User profile updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}