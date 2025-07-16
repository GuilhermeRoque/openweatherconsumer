# Load environment variables from .env file
ifneq ("$(wildcard .env)","")
include .env
endif

# Export variables from .env file
export $(shell sed 's/=.*//' .env)

# Raise error if there isn't a real value for OPENWEATHER_APIKEY
check-env:
	@echo "Checking environment variables..."
	@if [ -z "$$OPENWEATHER_APIKEY" ]; then \
		echo "Error: OPENWEATHER_APIKEY is not set"; \
		exit 1; \
	elif [ "$$OPENWEATHER_APIKEY" = "my_api_key" ]; then \
		echo "Error: OPENWEATHER_APIKEY is set to the mock value"; \
		exit 1; \
	else \
		echo "OPENWEATHER_APIKEY is set to $$OPENWEATHER_APIKEY"; \
	fi

clean:
	docker-compose down --volumes --remove-orphans

all: check-env
	@echo "Building and starting docker containers"
	docker-compose up --build

test-start-infra:
	docker network create network-test
	docker run -d --name mongodb-test --network network-test -p 27017:27017 mongo:7.0.14-jammy

test-stop-infra:
	docker stop mongodb-test
	docker rm mongodb-test
	docker network rm network-test

test-build-img:
	docker build --file app_test.dockerfile -t openweather_test:latest .

test-run:
	-docker run -e MONGO_URL=mongodb://mongodb-test:27017/ --name openweather_test --network network-test -v ./app:/app openweather_test:latest
	docker rm openweather_test

test-run-it:
	docker run -e MONGO_URL=mongodb://mongodb-test:27017/ --name openweather_test --network network-test -it -v ./app:/app openweather_test:latest /bin/bash

test-run-server:
	docker run -e MONGO_URL=mongodb://mongodb-test:27017/ --name openweather_test --network network-test -it -v ./app:/app -p 8000:8000 openweather_test:latest uvicorn main:app --host 0.0.0.0 --port 8000 --reload