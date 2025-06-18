from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from firebase_admin import db, initialize_app
from backend.services.FirebaseServices import initialize_firebase
from backend.services.bulk_message_sender import bulk_message_main

initialize_firebase()

# This function will fetch all user's location
target_latitude = '5.65198'
target_longitude = '6.651984'

async def fetch_all_user():
    try:
        print('fetch all location')
        ref = db.reference('users')
        user_data = ref.get()
        
        # This function will filter all user's that resides near the reported location
        recepient = users_location_validator(user_data,target_latitude,target_longitude)

        # This function will pass the data to bulk sms sender to notify all users on the target location
        await bulk_message_main(recepient)
        print('Finished running the bulk sms sender')

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        ) 
    
# This function will separate the users that are belong to the target location
def users_location_validator(user_data,target_latitude,target_longitude):
    try:
        for each_data in user_data['location']:
            if each_data.latitude < target_latitude and each_data.longitude < target_longitude:
                print(each_data)
                recepient = each_data.contact_number
                return recepient
            else:
                return

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )