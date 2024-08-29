from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import read_task
from tasks import task_get_cities_weather

app = FastAPI()

class StartTaskRequest(BaseModel):
    user_id: str

class GetTaskResponse(BaseModel):
    user_id: str
    task_id: str
    status: str
    progress: int
    timestamp: datetime
    results: list

class StartTaskResponse(BaseModel):
    task_id: str

def run_task(user_id:str) -> str:
    task = task_get_cities_weather.delay(user_id)
    return task.id


@app.post("/openweather", response_model=StartTaskResponse)
async def start_task(request: StartTaskRequest):
    task_id = run_task(request.user_id)
    return StartTaskResponse(task_id=task_id)

@app.get("/openweather/{user_id}", response_model=GetTaskResponse)
async def get_task(user_id: str):
    request = read_task(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
