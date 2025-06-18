from fastapi import APIRouter,FastAPI,WebSocket, WebSocketDisconnect,HTTPException
from backend.controllers.website.login_page.login import loginhandler
from backend.controllers.website.login_page.forgotPassword import forgotPasswordHandler
from backend.controllers.website.login_page.signup import createAccountHandler 
from backend.services.data_models import CreateAccountData,SaveLogs
from backend.controllers.website.login_page.save_logs import save_logs_to_db
from backend.services.remove_previous_logs import remove_previous_logs
from pydantic import BaseModel
import json

router = APIRouter()

class LoginCredential(BaseModel):  
    idToken: str

@router.post("/login")
async def handleLogin(user:LoginCredential):
    idToken = user.idToken
    try:
        return await loginhandler(idToken)
    except HTTPException as e:
         print(f"Error during login: {e.detail}")
         raise e

@router.post("/forgot-password")
async def forgotPasswordhandler(email:str):
    return await forgotPasswordHandler(email)

@router.post("/save_logs")
async def save_logs(data: SaveLogs):
    print('Backend hit')

    try:
            await remove_previous_logs()
            log_result = await save_logs_to_db(data.dict())
            if log_result:
                return {"message": "Logs saved successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while saving logs.")
    
    except HTTPException as e:
         print(f"Error during login: {e.detail}")
         raise e

@router.post("/create-account")
async def create_account(data: CreateAccountData):
    print('Backend hit')
    try:
        id_token = data.idToken
        name = data.name
        role = data.role
        user_type = data.userType
        age = data.age
        sex = data.sex
        longitude = data.longitude
        latitude = data.latitude
        contact_number = data.contactNumber
        create_data = data.dict()
        return await createAccountHandler(create_data)
    
    except HTTPException as e:
        print(f"Error during account creation: {e.detail}")
        raise e
    