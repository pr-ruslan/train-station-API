# Train Station API

A Django REST API for managing stations, trains, routes, crew, journeys,
and orders.\
This project is fully containerized with **Docker** and uses
**PostgreSQL** as its database.

------------------------------------------------------------------------

## 🚀 Features

-   Django REST Framework API
-   PostgreSQL database
-   Dockerized development environment
-   Custom Django management command `wait_for_db`
-   Automatic migrations on startup
-   Modular architecture (Stations, Trains, Routes, Journeys, Orders)
-   Ready for deployment

------------------------------------------------------------------------

## 📦 Project Structure

    train-station-API/
    │── station/                      # Main Django app
    │   ├── models/                   # Database models
    │   ├── serializers/              # API serializers
    │   ├── views/                    # API views
    │   ├── urls.py                   # App URL routes
    │   ├── management/
    │   │   ├── commands/
    │   │   │   └── wait_for_db.py    # Wait for DB before starting server
    │── train_station_api/            # Project settings
    │── Dockerfile
    │── docker-compose.yml
    │── requirements.txt
    │── README.md

------------------------------------------------------------------------

## 🐳 Running the Project With Docker

### 1️⃣ Build and start containers

``` bash
docker-compose up --build
```

### 2️⃣ Stop all containers

``` bash
docker-compose down
```

### 3️⃣ Stop and remove EVERYTHING (containers, volumes)

``` bash
docker-compose down -v
```

------------------------------------------------------------------------

## 🧰 Useful Docker Commands

### View running containers

``` bash
docker ps
```

### Run a command inside the app container

``` bash
docker exec -it train-station-api-app-1 bash
```

### Create Django superuser inside container

``` bash
docker exec -it train-station-api-app-1 python manage.py createsuperuser
```

------------------------------------------------------------------------

## 🛠 Dockerfile Overview

``` dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y     libpq-dev gcc --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

------------------------------------------------------------------------

## 🐘 PostgreSQL Configuration

### In `docker-compose.yml`:

``` yaml
db:
  image: postgres:17.6-alpine3.19
  environment:
    POSTGRES_DB: postgres
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  ports:
    - "5433:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

------------------------------------------------------------------------

## 🧩 Custom Management Command

### `wait_for_db.py`

Ensures the Django app waits until PostgreSQL is ready.

``` python
from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError
from django.db import connections

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting for database...")

        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write("Database unavailable, retrying...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database is ready!"))
```

------------------------------------------------------------------------

## 🧪 Running Tests

``` bash
docker exec -it train-station-api-app-1 pytest
```

------------------------------------------------------------------------

## 📄 License

MIT License\
Feel free to modify and use as needed.

------------------------------------------------------------------------