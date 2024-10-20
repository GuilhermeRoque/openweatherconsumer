import uuid
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from db import count_task_progress
from db import read_task, read_task_in_progress
from tasks import task_get_cities_weather
import secrets
import jwt
import datetime

app = FastAPI()
MAX_USERS = 10
SECRET_KEY = secrets.token_hex(32)  # Generates a secure random 64-character hex string
ALGORITHM = 'HS256'

origins = [
    "http://localhost:3000",  # Adjust this to your frontend's address
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

async def _authenticate_user(authorization):
    try:
        payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
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
async def start_task(request: StartTaskRequest, authorization: str = Header(None)):
    user_id = await _authenticate_user(authorization)
    task = read_task_in_progress(user_id=user_id)
    if task:
        raise HTTPException(status_code=400, detail="The user already owns a task in progress")
    task_id = run_task(user_id, request.cities)
    return StartTaskResponse(task_id=task_id)


@app.get("/openweather", response_model=GetTaskResponse)
async def get_task(authorization: str = Header(None)):
    user_id = await _authenticate_user(authorization)

    request = read_task(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request