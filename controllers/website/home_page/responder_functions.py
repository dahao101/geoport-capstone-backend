from fastapi import HTTPException, status
from firebase_admin import auth, db,exceptions as firebase_exceptions
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def create_responder_account(data):
    try:
        store_data = auth.create_user(
            email=data.email,
            password=data.password
        )
        
        user_id = store_data.uid

        ref = db.reference(f'users/{user_id}')

        data_to_save = {
            "contactNumber": data.number,
            "name": data.name,
            "role": "Responder"
        }
        
        ref.set(data_to_save)

        return {
            "status": "success",
            "message": "Responder account successfully created",
            "uid": user_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account creation failed: {str(e)}"
        )
async def fetch_responder_data():
    try:
        ref = db.reference('users')
        data = ref.get()

        responder_data = []
        if data:
            for user_id, user_info in data.items():
                if user_info.get("role") == "Responder":
                    auth_data = auth.get_user(user_id) 
                    responder_data.append({
                        "id": auth_data.uid,
                        "email": auth_data.email,
                        "name": user_info.get("name"),
                        "phone": user_info.get("contactNumber"),
                        "disabled": auth_data.disabled
                    })

  
        return {
            "status": "success",
            "data": responder_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Something went wrong while fetching user data: {str(e)}"
        )


async def disable_responder(data):
    try:
        status_bool = data.status.lower() == "true"
        auth.update_user(data.user_id, disabled=status_bool)
        return {"status": "success" }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Something went wrong while fetching user data: {str(e)}"
        )
    

async def remove_responder(user_id):
    try:
        print('data to be deleted',user_id)
        auth.delete_user(user_id)
        user_ref = db.reference(f'users/{user_id}')
        user_ref.delete()
        return {"status": "success" }
    except firebase_exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Firebase error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
    


async def login_responder_checker(user_id):
    try:
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get()

        if user_data and user_data.get("role") == "Responder":
            return {"status": "success"}
        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User not authorized: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking user role: {str(e)}"
        )

async def update_responder(data):
    try:
        print(data)
        updated_user = auth.update_user(
            uid=data.id,
            email=data.updateEmail
        )

        ref = db.reference(f'users/{data.id}')
        ref.update({
            "contactNumber": data.phone,
            "name": data.name
        })

        return {
            "status": "success",
            "message": "Responder updated successfully",
            "auth_uid": updated_user.uid
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating responder: {str(e)}"
        )