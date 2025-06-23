import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os


#Grab all information from the .env file 
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key")
print(SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 60))



#Create a JWT token using the information for the env file 
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY,algorithm =ALGORITHM)

#Decodes a JWT Token using the information from the env file
def decode_token(token:str):
    try:
        print(token)
        return jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail= "Invalid Token")