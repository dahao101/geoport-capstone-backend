import firebase_admin
import os
from dotenv import load_dotenv
from firebase_admin import credentials, db

firebase_config = {
    "apiKey": "AIzaSyD4kljPvbropwmMLLVz2YJGLIvd7zaC9YU",
    "authDomain": "geoport-malaybalay.firebaseapp.com",
    "databaseURL": "https://geoport-malaybalay-default-rtdb.firebaseio.com",
    "projectId": "geoport-malaybalay",
    "storageBucket": "geoport-malaybalay.firebasestorage.app",
    "messagingSenderId": "952130231721",
    "appId": "1:952130231721:web:1f5e2c5a59200b98d878b8",
    "measurementId": "G-29WH43R22W"
}

cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_KEY_PATH"))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })

ref = db.reference('/somepath')
data = ref.get()
print(data)
