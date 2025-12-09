# Train Station API

A Django REST API for managing **stations, trains, routes, journeys,
crew, and orders**.\
The project is fully containerized with **Docker** and uses
**PostgreSQL** as its database.

------------------------------------------------------------------------

## 📥 Installation (From GitHub)

### 1. Clone the repository and install requirements

``` bash
git clone https://github.com/pr-ruslan/train-station-API.git
cd train-station-API
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 2. If you run app manually
Edit your db settings in settings.py

Migrate and run application:

``` bash
python manage.py migrate
python manage.py runserver
```

### 3. Start the project with Docker

``` bash
docker-compose up --build
```

The API will be available at:\
👉 **http://localhost:8000**

------------------------------------------------------------------------

## 🐳 Docker Commands

If you need a sample data to test application:

``` bash
docker-compose exec app python manage.py loaddata  sample_data.json
```

Stop containers:

``` bash
docker-compose down
```

Stop & remove ALL containers + volumes:

``` bash
docker-compose down -v
```

Create a Django superuser:

``` bash
docker exec -it train-station-api-app-1 python manage.py createsuperuser
```

------------------------------------------------------------------------

## 🧪 Running Tests

``` bash
docker exec app python manage.py test
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

## 📄 License

MIT License.\
Feel free to use and modify.

------------------------------------------------------------------------
