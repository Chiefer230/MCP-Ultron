from fastapi import FastAPI , Request, HTTPException
from pydantic import BaseModel
from ultron_agent import process_task
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from jwt_authentication import create_token , decode_token
import json
import datetime
import os

app = FastAPI()

load_dotenv()

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
FERNET_KEY = os.getenv("FERNET_KEY")
MCP_PORT = os.getenv("MCP_PORT")


print(FERNET_KEY)
print(SECRET_TOKEN)

fernet = Fernet(FERNET_KEY)

class LoginForm(BaseModel):
    username:str
    ip_address: str
    mac_address: str


"""
Login function for creating JWTs for Ultron's IOT devices.
His login features include his name, ip address, and his mac address to ensure its the correct device
A payload is constructed for token generation
"""
@app.post("/login")
async def login(form : LoginForm):
    print(FERNET_KEY)
    print(SECRET_TOKEN)
    if form.username == "Ultron" and form.ip_address == "host" and form.mac_address == "pi":
        user = {
            "sub": form.username
        }
        print("Login Done")
        token = create_token(user)
        print("LOGIN SUCCESSFUL", token)
        return token
    
    else:
        raise HTTPException(status_code=401, detail= "Invalid Credentials")


"""
Token Validation Once the Token is generated for the connected IOT Device
Takes the Authorization header, checks for token 
"""
@app.middleware("http")
async def validate_token(request:Request, call_next):
    if request.url.path == "/login":
        return await call_next(request)
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Missing or Invalid Token")
    
    token = auth_header.split(" ")[1]
    print(token)
    decode_token(token)

    return await call_next(request)

class EncryptedRequest(BaseModel):
    payload:str

"""
MCP Server Logic taking a encrpyted request 

"""
@app.post("/mcp")
async def handle_mcp(encrytped_request: EncryptedRequest):
    try:
        decrypted_data = fernet.decrypt(encrytped_request.payload.encode()).decode()
        req_data = json.loads(decrypted_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed:{e}")
    
    task = req_data.get("task")
    context = req_data.get("context")
    spoken_command = req_data.get("input",{}).get("spoken_command","")


    print("[[[[[Recieved", spoken_command)

    result = process_task(task,context,spoken_command)

    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "task": task,
        "context": context,
        "input" : req_data.get("input"),
        "result" : result
    }

    os.makedirs("logs", exist_ok=True)
    with open ("logs/mcp_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {"response" : result}