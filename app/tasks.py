import time

from celery import Celery

from db import insert_request, update_request

celery_app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery_app.task(bind=True)
def add(self, user_id: str, x: int, y: int):
    insert_request(
        user_id=user_id,
        task_id=self.request.id
    )
    for i in range(10):
        progress = i * 10
        time.sleep(5)
        update_request(
            user_id=user_id,
            progress=progress,
            new_result=i,
            status="PROGRESS" if i < 9 else "DONE"
        )
    return x + y