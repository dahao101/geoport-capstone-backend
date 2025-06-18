from fastapi.responses import *
from fastapi import *
from firebase_admin import auth
from typing import Dict
import json
from backend.controllers.application.homepage.responderLoginValidator import responderValidator
from pydantic import BaseModel

 
router = APIRouter()
active_connections = {}


@router.post('/check-responder-validity/{id}')
async def check_responder_account(id:str,authorization: str = Header(None)):
    print('responder checker reached')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        result = await responderValidator(id)
        return result

    except HTTPException as e:
        return JSONResponse(content={ "status": "error","message": e.detail},status_code=e.status_code)

    except Exception as e:
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
