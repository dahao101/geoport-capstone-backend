from fastapi import HTTPException, status
import firebase_admin
from firebase_admin import credentials, auth, db
from backend.services.FirebaseServices import  initialize_firebase



initialize_firebase()

async def verify_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

async def createAccountHandler(additional_data: dict):
    
    required_fields = ["idToken", "name", "role", "userType", "age", "sex", "longitude", "latitude", "contactNumber"]
    
    for field in required_fields:
        if field not in additional_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    id_token = additional_data.get("idToken")
    decoded_token = await verify_token(id_token)
    uid = decoded_token.get("uid")

    ref = db.reference(f'users/{uid}')
    
    try:
        ref.set(
            {
                "name": additional_data.get("name"),
                "role": additional_data.get("role"),
                "userType": additional_data.get("userType"),
                "age": additional_data.get("age"),
                "sex": additional_data.get("sex"),
                "location": {
                    "longitude": additional_data.get("longitude"),
                    "latitude": additional_data.get("latitude"),
                },
                "contactNumber": additional_data.get("contactNumber")
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
