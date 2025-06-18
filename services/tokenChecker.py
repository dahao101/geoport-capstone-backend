import jwt
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')


class TokenChecker:
    def decodeToken(self,token):
        secret_key = os.getenv("SECRET_KEY")
        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")