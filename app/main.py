from fastapi import FastAPI
from pydantic import BaseModel
from tasks import add, celery_app

app = FastAPI()

class Operators(BaseModel):
    x: int
    y: int

@app.post("/tasks/add/")
async def add_task(operators: Operators) -> dict:
    task_id = add.delay(operators.x, operators.y)
    return {"task_id": task_id.id}

@app.get("/tasks/{task_id}/")
async def get_task_result(task_id: str) -> dict:
    task_result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": task_result.status, "result": task_result.result}