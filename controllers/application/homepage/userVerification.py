from fastapi import HTTPException, status
from backend.services.FirebaseServices import initialize_firebase
from firebase_admin import auth, db

# ✅ Initialize Firebas
initialize_firebase()

async def updateuserStatus(userId: str, image_url: str):
    print("🔄 Updating user status...")
    print(f"🆔 User ID: {userId}")

    try:
        try:
            auth.get_user(userId)
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in Firebase Authentication"
            )
        ref = db.reference(f'users/{userId}')
        user_record = ref.get()

        if not user_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User data for {userId} not found in database"
            )

        ref.update({
            "status": "verified",
            "image": image_url
        })

        print("✅ User status updated successfully!")
        return {"success": True, "message": "User status updated successfully!"}

    except HTTPException as e:
        print(f"❌ HTTP Error: {e.detail}")
        raise e  
    except Exception as e:
        print(f"❌ Error updating user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user data: {str(e)}"
        )
