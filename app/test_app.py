import datetime
import uuid
from random import random

from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from requests import Response

from db import read_task, insert_task
from tasks import task_get_cities_weather
from main import app

client = TestClient(app)

@patch("main.run_task")
@patch("main._authenticate_user")
def test_post_request_endpoint(run_task_mock, auth_mock):
    user_id = str(uuid.uuid4())
    auth_mock.return_value = user_id
    mock_task_id = str(uuid.uuid4())
    run_task_mock.return_value = mock_task_id
    response = client.post("/openweather", json={"cities": ["Rio de Janeiro", "Brasília"]})
    assert response.status_code == 200

@patch("main._authenticate_user")
def test_post_request_endpoint_error_duplicated(auth_mock):
    user_id = str(uuid.uuid4())
    auth_mock.return_value = user_id
    mock_task_id = str(uuid.uuid4())
    insert_task(user_id=user_id, task_id=mock_task_id)
    response = client.post("/openweather", json={"cities": ["Rio de Janeiro", "Brasília"]})
    assert response.status_code == 400

def test_get_request_endpoint_not_found():
    user_id = str(uuid.uuid4())
    response = client.get(f"/openweather/{user_id}")
    assert response.status_code == 404


@patch("main._authenticate_user")
@patch("main.read_task", return_value=1)
def test_get_request_endpoint(get_request_mock, auth_mock):
    user_id = str(uuid.uuid4())
    auth_mock.return_value = user_id
    mock_task_id = str(uuid.uuid4())
    mock_request = {
        "user_id": user_id,
        "task_id": mock_task_id,
        "timestamp": datetime.datetime.utcnow(),
        "results": [],
        "status": "PROGRESS",
        "progress": 0
    }
    get_request_mock.return_value = mock_request
    response = client.get(f"/openweather")
    assert response.status_code == 200

    response_payload = response.json()
    assert mock_request["user_id"] == response_payload["user_id"]
    assert mock_request["task_id"] == response_payload["task_id"]

@patch("main._authenticate_user")
@patch("tasks.request_city_weather")
def test_task_get_cities_weather(request_weather_mock, auth_mock):
    user_id = str(uuid.uuid4())
    auth_mock.return_value = user_id
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "main": {
            "temp": random() * 100,
            "humidity": random() * 100
        }
    }
    request_weather_mock.return_value = mock_response
    task_get_cities_weather(user_id=user_id, cities=["Rio de Janeiro", "Brasília", "São Paulo"])
    log_request = read_task(user_id=user_id)

    assert log_request is not None
    assert log_request["status"] == "DONE"
    assert log_request["progress"] == 100
    assert len(log_request["results"]) == 3


@patch("main._authenticate_user")
@patch("tasks.request_city_weather")
def test_task_get_cities_weather_error_request(request_weather_mock, auth_mock):
    user_id = str(uuid.uuid4())
    auth_mock.return_value = user_id
    mock_response = Mock(spec=Response)
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": "Internal Server Error"
    }
    request_weather_mock.return_value = mock_response
    task_get_cities_weather(user_id=user_id, cities=["Rio de Janeiro", "Brasília", "São Paulo"])
    log_request = read_task(user_id=user_id)

    assert log_request is not None
    assert log_request["status"] == "FAILED"
    assert log_request["progress"] == 0
    assert len(log_request["results"]) == 0
    assert log_request["user_id"] == user_id

def test_get_user_id():
    response = client.get("/userid")
    assert response.status_code == 200
    content = response.json()
    assert content['user_id'] is not None
    assert content['token'] is not None

@patch("main.run_task")
def test_post_with_auth(run_task_mock):
    response = client.get("/userid")
    assert response.status_code == 200
    content = response.json()
    user_id = content["user_id"]
    token = content["token"]
    mock_task_id = str(uuid.uuid4())
    run_task_mock.return_value = mock_task_id
    response = client.post("/openweather", json={"cities": ["Rio de Janeiro", "Brasília"]}, headers={"Authorization": token})
    assert response.status_code == 200