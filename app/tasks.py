import logging
import math
import os
import re
import time
import requests
from celery import Celery
from requests import Response

from db import insert_request, update_request, abort_request

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
openweather_url = os.getenv('OPENWEATHER_URL', 'https://api.openweathermap.org/data/2.5/')
openweather_apikey = os.getenv('OPENWEATHER_APIKEY')
city_codes = "city_codes.txt"

celery_app = Celery(
    'tasks',
    broker=broker_url,
    backend=broker_url
)

def read_city_codes():
    with open(city_codes) as f:
        content = f.read()
    return content

@celery_app.task(bind=True)
def task_get_cities_weather(self, user_id: str):
    insert_request(
        user_id=user_id,
        task_id=self.request.id
    )
    city_codes_content = read_city_codes()
    codes = re.sub(r'\s+', '', city_codes_content).split(",")
    len_codes = len(codes)
    for i, code in enumerate(codes):
        response = request_city_weather(code)
        if response.status_code != 200:
            logging.error(f"Code {code} Status {response.status_code} Text: {response.text}")
            abort_request(user_id=user_id)
            break
        payload = response.json()
        temp = payload['main']['temp']
        humidity = payload['main']['humidity']
        progress = math.ceil(i/(len_codes - 1) * 100)
        update_request(
            user_id=user_id,
            progress=progress,
            new_result={"id": code, "temperature": temp, "humidity": humidity},
            status="PROGRESS" if i < len_codes - 1 else "DONE"
        )
        time.sleep(1) # sleep 1 sec between iteration to not reach the 60 requests per minute limit


def request_city_weather(code: str) -> Response:
    path = f"{openweather_url}weather?id={code}&appid={openweather_apikey}"
    response = requests.get(path)
    return response