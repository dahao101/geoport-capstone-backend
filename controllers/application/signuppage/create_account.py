import firebase_admin
from firebase_admin import  db, credentials

cred = credentials.Certificate("../../../geoport-malaybalay-firebase-adminsdk-bhb9k-af9743f001.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geoport-malaybalay-default-rtdb.firebaseio.com'
})



async def create_user_account(data):
    try:
        
        
        info_to_save = db.reference(f'users/{data.uid}')
        info_to_save.set({
            "name": data.name,  
            "age":data.age,
            "sex":data.sex,
            "contactNumber": data.contact_number,
            "role": "User",
            "status": data.status,
        })
        return {"message": "User created successfully", "uid": data.uid}



    except Exception as e:
        return {"error": str(e)}


    
