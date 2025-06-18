from fastapi import HTTPException, status
from datetime import datetime
from firebase_admin import db

async def expired_key_remover():
    print('expired key checker is running ')
    try:
        ref = db.reference('temporary_keys') 
        data = ref.get() 

        if data is None:
            print("No data found in 'temporary_keys' collection.")
            return

        current_time = datetime.now() 

        if isinstance(data, dict):  
            for unique_id, record in data.items():  
                expiration_time_str = record.get('expiration_time') 

                if expiration_time_str:
                    try:
                        expiration_time = datetime.fromisoformat(expiration_time_str)
                    except ValueError as e:
                        print(f"Invalid expiration_time format for {unique_id}: {e}")
                        continue

                    if expiration_time < current_time:
                        print(f"Removing expired record with unique ID: {unique_id}, expired at {expiration_time}")
                        ref.child(unique_id).delete()  
                    else:
                        print(f"Record with unique ID {unique_id} is still valid, expires at {expiration_time}")
        else:
            print("Data format in 'temporary_keys' is not a dictionary.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
