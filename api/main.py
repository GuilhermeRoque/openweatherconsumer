from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.db import get_request
from api.tasks import task_get_cities_weather

app = FastAPI()

class RequestModel(BaseModel):
    user_id: str

class ResponseModel(BaseModel):
    user_id: str
    task_id: str
    status: str
    progress: int
    timestamp: datetime
    results: list

def run_task(user_id):
    task = task_get_cities_weather.delay(user_id)
    return task.id

@app.post("/openweather")
async def add_task(request: RequestModel) -> dict:
    task_id = run_task(request.user_id)
    return {"task_id": task_id}

@app.get("/openweather/{user_id}", response_model=ResponseModel)
async def get_task_result(user_id: str) -> dict:
    request = get_request(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
