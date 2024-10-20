import logging
import math
import os
import time
import requests
from celery import Celery
from requests import Response
import json
from db import insert_task, update_task, abort_task

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
openweather_url = os.getenv('OPENWEATHER_URL', 'https://api.openweathermap.org/data/2.5/')
openweather_apikey = os.getenv('OPENWEATHER_APIKEY')
city_codes = "city_codes.txt"
city_map = json.load(open("city_map.json"))

celery_app = Celery(
    'tasks',
    broker=broker_url,
    backend=broker_url
)

def read_city_codes() -> str:
    with open(city_codes) as f:
        content = f.read()
    return content

@celery_app.task(bind=True)
def task_get_cities_weather(self, user_id: str, cities: list[str]):
    insert_task(
        user_id=user_id,
        task_id=self.request.id
    )
    code_names = [(city_map[city]["id"], city) for city in cities]
    len_codes = len(code_names)
    for i, code_name in enumerate(code_names):
        response = request_city_weather(code_name[0])
        if response.status_code != 200:
            logging.error(f"City {code_name} Status {response.status_code} Text: {response.text}")
            abort_task(user_id=user_id)
            continue
        payload = response.json()
        temp = payload['main']['temp']
        humidity = payload['main']['humidity']
        progress = math.ceil(i/(len_codes - 1) * 100) if len_codes > 1 else 100
        update_task(
            user_id=user_id,
            progress=progress,
            new_result={"name": code_name[1], "temperature": temp, "humidity": humidity},
            status="PROGRESS" if i < len_codes - 1 else "DONE"
        )
        time.sleep(1) # sleep 1 sec between iteration to not reach the 60 requests per minute limit


def request_city_weather(code: str) -> Response:
    path = f"{openweather_url}weather?id={code}&appid={openweather_apikey}&units=metric"
    response = requests.get(path)
    return response
