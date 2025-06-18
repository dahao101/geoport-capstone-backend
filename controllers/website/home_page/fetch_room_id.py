from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from fastapi.responses import JSONResponse
from backend.services.FirebaseServices import  initialize_firebase

initialize_firebase()
async def feth_users_room_id(user_id):
    try:
        print(user_id)
        ref = db.reference(f'generated_room_id/{user_id}')
        room_id = ref.get()
        
        if not room_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No room ID found for this user."
            )

        return {"status": "success", "data": room_id}


    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching reports: {str(e)}"
        )
