# OpenWeather Service

## Description

This application consumes the OpenWeather API to retrieve weather information based on city names, like 'São Paulo' or 'Rio de Janeiro', which are listed in `app/city_map.json`.

**Usage**

- Get a token by executing a GET request on `/userid`
- Start an async task by executing a POST request on `/openweather` and passing city names on the request body. This will start a background task to request the cities weather information.
- Get the task result by executing a GET request on `/openweather`. This will return the current retrieved weather information and the task current status. 

**Notes**

- See details about API in the Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) after running the application.

## Prerequisites

Before you begin, ensure you have the following:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [OpenWeather API Key](https://home.openweathermap.org/api_keys)

**IMPORTANT**: Before running the application, you must replace the **OPENWEATHER_APIKEY** value in **.env.sample** with a real API key and then rename the file to **.env**.

## Commands

The Makefile includes several commands. The most important are:

- `make all`: Runs the application using Docker Compose.
- `make clean`: Stops and removes the containers.
- `make test-start-infra`: Starts a database container to prepare for running the tests.
- `make test-build-img`: Builds a Docker image for running the tests.
- `make test-run`: Runs the tests.

**Notes**: 
- If you can't use make because you aren't in a Linux system you can copy and paste the commands in the file Makefile

### Summary

- To run the application, execute `make all`. Afterward, you can access the REST API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- To check test coverage for the first time, run `make test-start-infra`, followed by `make test-build-img`, and finally `make test-run`.

## Stack

Here are the key technologies used in this project:

- **FastAPI**: Chosen for building the REST API due to its performance and automatic API documentation. It also supports dependency injection and asynchronous operations.
- **MongoDB**: Used for persisting request results. MongoDB was selected for its scalability, as complex database queries and relationships are not required.
- **Celery**: Utilized for running asynchronous tasks. While the current requirements do not involve complex asynchronous task handling, Celery provides a robust solution for potential future needs.
- **Redis**: Serves as the broker for asynchronous tasks. It is simpler and more lightweight compared to other broker options, such as AMQP.
- **Pytest**: Chosen for automated testing due to its simplicity compared to `unittest.TestCase` classes.
- **NGINX**: Reverse proxy for the application. This allows the creation of application replicas.

## Deploy
Deploy is defined in the docker-compose.yml file, which is called by "make all" command and will run the following:
- 1 API instances
- 1 celery workers instances, which runs 5 workers each
- 1 MongoDB instance
- 1 Redis instance
- 1 NGINX instance