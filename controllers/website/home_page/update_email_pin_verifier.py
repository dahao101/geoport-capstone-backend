from backend.services.email_templates.pin_verification import pin_sender_template
from backend.services.expired_key_checker import expired_key_remover
from backend.services.pin_generator import create_pin
from backend.services.email_sender import emailSender
from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime
from firebase_admin import db


async def update_email_verify_pin(db_id: str, inputted_pin: str):

    try:
        ref = db.reference(f'temporary_keys/{db_id}')
        
        stored_data = ref.get()  
        if not stored_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temporary key not found.")
        
        stored_pin = stored_data.get('generated_pin')
        expiration_time_str = stored_data.get('expiration_time')
        
        if not stored_pin or not expiration_time_str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing pin or expiration time.")

        print(f"Stored pin: {stored_pin}, Expiration time: {expiration_time_str}")

        print(stored_pin)
        print(inputted_pin)
        if not checker_function(stored_pin, inputted_pin):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The entered PIN does not match the stored PIN.")
        
        if not expiration_checker(expiration_time_str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The expiration time has passed.")
        
        return True 
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")




def checker_function(stored_pin, inputted_pin):
    stored_pin = str(stored_pin).strip()
    inputted_pin = str(inputted_pin).strip()
    try:
        if stored_pin != inputted_pin:
            print("pin don't matched")
            return False
        else:
            print('PIN matched!')
            return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")




def expiration_checker(expiration_time_str):
    try:
        expiration_time = datetime.fromisoformat(expiration_time_str)
        current_time = datetime.now()
        
        if expiration_time < current_time:
            print(f"Expiration time {expiration_time} has passed.")
            return False
        else:
            print('Time is still valid.')
            return True
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")

