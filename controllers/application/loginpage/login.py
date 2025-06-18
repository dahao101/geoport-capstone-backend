from fastapi import HTTPException, status
import firebase_admin
from firebase_admin import auth, db
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def createUserAccountHandler(user_data: dict):
    required_fields = ["idToken", "name", "age", "sex", "longitude", "latitude", "contactNumber"]

    # Validate required fields
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    id_token = user_data.get("idToken")
    
    try:
        # Verify ID token and get UID
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get("uid")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Token: {str(e)}")

    # Reference to Firebase Realtime Database
    user_ref = db.reference(f'users/{uid}')

    try:
        # Set user data in Realtime Database
        user_ref.set({
            "name": user_data.get("name"),
            "role": "User",  
            "age": user_data.get("age"),
            "sex": user_data.get("sex"),
            "location": {
                "longitude": user_data.get("longitude"),
                "latitude": user_data.get("latitude"),
            },
            "contactNumber": user_data.get("contactNumber"),
            "createdAt": user_data.get("createdAt", "2025-03-13")  # Auto timestamp (can use datetime module)
        })
        return {"message": "User account created successfully", "uid": uid}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
