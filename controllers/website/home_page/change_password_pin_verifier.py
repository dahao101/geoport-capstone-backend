from fastapi import HTTPException, status
from firebase_admin import db, auth
from datetime import datetime
import traceback

async def change_password_verify_pin(pin: str, id: str):
    try:
        try:
            user = auth.get_user(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not registered"
            )

        user_id = user.uid
        temp_data_ref = db.reference(f'temporary_keys/{user_id}')
        temp_data = temp_data_ref.get()

        if not temp_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No PIN data found for this user"
            )

        stored_pin = temp_data.get("generated_pin")
        expiration_timestamp = temp_data.get("expiration_time")

        if not stored_pin or not expiration_timestamp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid temporary key data structure"
            )

        try:
            expiration_time = datetime.fromisoformat(expiration_timestamp)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid expiration time format"
            )

        current_time = datetime.utcnow()

        if current_time > expiration_time:
            temp_data_ref.delete()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN has expired"
            )

        if str(stored_pin) == str(pin):
            temp_data_ref.delete()
            return True  


        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect PIN"
        )

    except HTTPException:
        raise  # Let FastAPI handle known HTTP errors

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
