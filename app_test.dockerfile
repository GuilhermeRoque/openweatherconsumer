FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_test.txt .

RUN pip install --no-cache-dir -r requirements_test.txt

COPY ./app .
COPY .coveragerc .

CMD ["pytest", "--cov", "--cov-config=.coveragerc"]