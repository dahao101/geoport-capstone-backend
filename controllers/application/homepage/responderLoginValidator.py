from fastapi import *
from firebase_admin import auth,db
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()
async def responderValidator(id:str):
    try:
        ref = db.reference(f'users/{id}')

        account = ref.get()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Responder account not found."
            )
        
        if account['role'] != "Responder":
            return {"status": "unsuccessful"}

        else:
            return {"status": "success"}
    except Exception as e:
        print(f"Error storing report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
