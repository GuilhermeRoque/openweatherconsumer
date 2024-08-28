from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_request
from tasks import get_all_cities_weather

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


@app.post("/openweather")
async def add_task(request: RequestModel) -> dict:
    task_id = get_all_cities_weather.delay(request.user_id)
    return {"task_id": task_id.id}

@app.get("/openweather/{user_id}", response_model=ResponseModel)
async def get_task_result(user_id: str) -> dict:
    request = get_request(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
