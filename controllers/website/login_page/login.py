from fastapi import HTTPException, status
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth,db
from backend.services.tokenGenerator import TokenGenerator
from backend.services.FirebaseServices import  initialize_firebase


load_dotenv()
initialize_firebase()

async def verify_token(id_token: str):
    try:
        print('token  ',id_token)
        decoded_token = auth.verify_id_token(id_token)
        if not decoded_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
        return decoded_token
    
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def loginhandler(idToken:str):
    decoded_token = await verify_token(idToken)
    user_id = decoded_token['uid']
    
    user_ref = db.reference(f'users/{user_id}')
    secret_key=os.getenv("SECRET_KEY")
    user_data = user_ref.get()
    
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User data not found.")

    role = user_data.get('role', 'Admin')
    custom_token = TokenGenerator().generateToken(user_id, role, secret_key)
    return {"user_id": user_id,"user_data": user_data,"token": custom_token}