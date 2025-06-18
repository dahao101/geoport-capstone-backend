from backend.services.email_templates.pin_verification import pin_sender_template
from backend.services.pin_generator import create_pin
from backend.services.email_sender import emailSender
from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import db, auth


async def send_pin_email(user_id: str, background_tasks: BackgroundTasks):
    try:
        print('backend reached during sending pin')
        ref = db.reference(f'users/{user_id}') 
        user_data = ref.get()  
        name = user_data.get('name')
        if not name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User name not found.")
        
        print(name)
        user = auth.get_user(user_id)
        email = user.email
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User email not found.")
        print(email)
        
        await check_db(user_id)

        # tawagon ang pin generator apil na expiration
        pin, expiration_time = create_pin()
        expiration_time_str = expiration_time.isoformat()
        # i set ang template sa email
        subject = 'UPDATE EMAIL PIN VERIFICATION'
        
        template = pin_sender_template(name, pin)
        background_tasks.add_task(emailSender, email, subject, template)

        # Save pin to Firebase after scheduling the email task
        save_pin = db.reference(f'temporary_keys')
        data = {'generated_pin': pin,'expiration_time':expiration_time_str}
        save_pin.child(user_id).set(data)
        
        return True 

    except Exception as e:
        print(f"Error in sending pin email: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")




async def check_db(user_id):
    ref = db.reference('temporary_keys') 
    result = ref.get()
    if result is None:
        print("No temporary_keys found. Collection doesn't exist yet.")
        return  
    
    if isinstance(result, dict) and not result:
        print("temporary_keys is empty.")
        return

    # If it's a non-empty dictionary or list, iterate over it
    if isinstance(result, dict):
        for key, record in result.items():
            print(f"Checking record: {record}")
            if record.get('reference_id') == user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIN ALREADY EXISTS.")
    elif isinstance(result, list):
        for record in result:
            if record.get('reference_id') == user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIN ALREADY EXISTS.")
