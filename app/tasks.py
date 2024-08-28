import logging
import math
import os
import re
import time
import requests
from celery import Celery

from db import insert_request, update_request, abort_request

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
openweather_url = os.getenv('OPENWEATHER_URL', 'https://api.openweathermap.org/data/2.5/')
openweather_apikey = os.getenv('OPENWEATHER_APIKEY')

celery_app = Celery(
    'tasks',
    broker=broker_url,
    backend=broker_url
)

@celery_app.task(bind=True)
def get_all_cities_weather(self, user_id: str):
    insert_request(
        user_id=user_id,
        task_id=self.request.id
    )
    with open("city_codes.txt") as f:
        codes = re.sub(r'\s+', '', f.read()).split(",")
        len_codes = len(codes)
        for i, code in enumerate(codes):
            path = f"{openweather_url}weather?id={code}&appid={openweather_apikey}"
            response = requests.get(path)
            if response.status_code != 200:
                logging.error(f"Path {path} Status {response.status_code} Text: {response.text}")
                abort_request(user_id=user_id)
                break
            payload = response.json()
            temp = payload['main']['temp']
            humidity = payload['main']['humidity']
            progress = math.ceil(i/len_codes * 100)
            update_request(
                user_id=user_id,
                progress=progress,
                new_result={"id": code, "temperature": temp, "humidity": humidity},
                status="PROGRESS" if i < len_codes else "DONE"
            )
            time.sleep(1) # sleep 1 sec between iteration to not reach the 60 requests per minute limit