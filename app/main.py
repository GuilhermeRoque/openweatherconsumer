from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_request
from tasks import add

app = FastAPI()

class Operators(BaseModel):
    x: int
    y: int
    user_id: str

class ResponseModel(BaseModel):
    user_id: str
    task_id: str
    status: str
    progress: int
    timestamp: datetime
    results: list


@app.post("/openweather")
async def add_task(operators: Operators) -> dict:
    task_id = add.delay(operators.user_id, operators.x, operators.y)
    return {"task_id": task_id.id}

@app.get("/openweather/{user_id}", response_model=ResponseModel)
async def get_task_result(user_id: str) -> dict:
    request = get_request(user_id=user_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
