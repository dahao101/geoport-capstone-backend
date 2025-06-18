import jwt
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='backend/.env')
secret_key = os.getenv("SECRET_KEY")

class TokenGenerator:

    def websitePayload(this,role,user_id,secret_key):
        expiration_time = datetime.utcnow() + timedelta(hours=15)
        payload = {
            "user_id": user_id,
            "role":  role,
            "expirationTime" :  expiration_time.isoformat()
        }
        return payload

    def generateToken(self,user_id, role,secret_key):      
        secret_key = str(secret_key)
        payload = self.websitePayload(user_id,role,secret_key)
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token

    