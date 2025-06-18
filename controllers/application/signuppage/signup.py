import firebase_admin
from firebase_admin import auth, db, credentials

# Initialize Firebase Admin (Make sure to configure this properly)
cred = credentials.Certificate("../../../geoport-malaybalay-firebase-adminsdk-bhb9k-af9743f001.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geoport-malaybalay-default-rtdb.firebaseio.com'
})

def create_user_manually(email: str, password: str, name: str, age: int, sex: str, contact_number: str):
    try:
        # 1️⃣ Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )
        
        uid = user.uid  # Get UID of the created user
        
        # 2️⃣ Store additional user details in Realtime Database
        user_ref = db.reference(f'users/{uid}')
        user_ref.set({
            "name": name,
            "age": age,
            "sex": sex,
            "contactNumber": contact_number,
            "role": "User",
            "userType": "Standard",
            "createdAt": "2025-03-13"
        })
        
        return {"message": "User created successfully", "uid": uid}
    
    except Exception as e:
        return {"error": str(e)}

# Example Usage:
response = create_user_manually(
    email="2201102996@student.buksu.edu.ph",
    password="password123",
    name="Mart Ervin Dahao",
    age=40,
    sex="Male",
    contact_number="09123456789"
)
print(response)
