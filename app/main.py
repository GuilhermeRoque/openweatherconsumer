import os
import uuid
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from db import count_task_progress
from db import read_task, read_task_in_progress
from tasks import task_get_cities_weather
import jwt
import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
MAX_USERS = 10
SECRET_KEY = os.getenv("SECRET_KEY", "MY_SECRET_KEY")
ALGORITHM = 'HS256'

security = HTTPBearer()

origins = [
    os.getenv('FRONT_ADDRESS', "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GetUserIdResponse(BaseModel):
    user_id: str
    token: str

class GetTaskResponse(BaseModel):
    user_id: str
    task_id: str
    status: str
    progress: int
    timestamp: datetime.datetime
    results: list

class StartTaskResponse(BaseModel):
    task_id: str

class StartTaskRequest(BaseModel):
    cities: list[str]

def run_task(user_id:str, cities: list[str]) -> str:
    task = task_get_cities_weather.delay(user_id, cities)
    return task.id

def decode_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject (user_id)",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (jwt.DecodeError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

@app.get("/userid", response_model=GetUserIdResponse)
async def get_user_id():
    if count_task_progress() >= MAX_USERS:
        raise HTTPException(status_code=503, detail="Max users reached. Please try again later")
    user_id = str(uuid.uuid4())
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }, SECRET_KEY, algorithm=ALGORITHM)
    return GetUserIdResponse(user_id=user_id, token=token)

@app.post("/openweather", response_model=StartTaskResponse)
async def start_task(request: StartTaskRequest, user_id = Depends(decode_jwt)):
    task = read_task_in_progress(user_id=user_id)
    if task:
        raise HTTPException(status_code=400, detail="The user already owns a task in progress")
    task_id = run_task(user_id, request.cities)
    return StartTaskResponse(task_id=task_id)

@app.get("/openweather", response_model=GetTaskResponse)
async def get_task(user_id = Depends(decode_jwt)):
    request = read_task(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request