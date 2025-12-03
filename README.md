# Train Station API

A Django REST API for managing **stations, trains, routes, journeys,
crew, and orders**.\
The project is fully containerized with **Docker** and uses
**PostgreSQL** as its database.

------------------------------------------------------------------------

## 📥 Installation (From GitHub)

### 1️⃣ Clone the repository

``` bash
git clone https://github.com/pr-ruslan/train-station-API.git
cd train-station-API
```

### 2️⃣ Start the project with Docker

``` bash
docker-compose up --build
```

The API will be available at:\
👉 **http://localhost:8000**

------------------------------------------------------------------------

## 🐳 Docker Commands

Start containers:

``` bash
docker-compose up --build
```

Stop containers:

``` bash
docker-compose down
```

Stop & remove ALL containers + volumes:

``` bash
docker-compose down -v
```

Run a command inside the app container:

``` bash
docker exec -it train-station-api-app-1 bash
```

Create a Django superuser:

``` bash
docker exec -it train-station-api-app-1 python manage.py createsuperuser
```

------------------------------------------------------------------------

## 🧪 Running Tests

``` bash
docker exec -it train-station-api-app-1 python manage.py test
```

Or using pytest:

``` bash
docker exec -it train-station-api-app-1 pytest
```

------------------------------------------------------------------------

## 🛠 Tech Overview

-   Python 3.12\
-   Django + Django REST Framework\
-   PostgreSQL\
-   Docker + docker-compose

### Project Structure

    train-station-API/
    │── station/                 # Main Django app
    │── train_station_api/       # Settings & configuration
    │── Dockerfile
    │── docker-compose.yml
    │── requirements.txt
    │── README.md

------------------------------------------------------------------------

## 🐘 PostgreSQL (from docker-compose.yml)

``` yaml
db:
  image: postgres:17.6-alpine3.19
  environment:
    POSTGRES_DB: postgres
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  ports:
    - "5433:5432"
```

------------------------------------------------------------------------

## 📄 License

MIT License.\
Feel free to use and modify.

------------------------------------------------------------------------
