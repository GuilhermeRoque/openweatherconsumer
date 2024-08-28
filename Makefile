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

