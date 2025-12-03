from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from station.models import (
    Station,
    TrainType,
    Train,
    Route,
    Journey,
    Order,
    Ticket,
)
from station.serializers import (
    TrainListSerializer,
    TrainDetailSerializer,
)

TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")


def sample_train(**params):
    train_type = TrainType.objects.create(name="maglev")
    defaults = {
        "name": "Sample train",
        "cargo_num": 10,
        "places_in_cargo": 20,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_route(**params):
    s1 = Station.objects.create(name="AAA", latitude=0, longitude=0)
    s2 = Station.objects.create(name="BBB", latitude=1, longitude=1)
    defaults = {
        "source": s1,
        "destination": s2,
        "distance": 100,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])


# ----------------------- UNAUTH TESTS -----------------------

class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ----------------------- TRAIN TESTS -----------------------

class AuthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        sample_train(name="Another train")

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.all().order_by("id")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_train_detail(self):
        train = sample_train()

        url = detail_url(train.id)
        res = self.client.get(url)

        serializer = TrainDetailSerializer(train)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


# ----------------------- JOURNEY CREATE TESTS -----------------------

class JourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_journey_successful(self):
        train = sample_train()
        route = sample_route()

        payload = {
            "train": train.id,
            "route": route.id,
            "departure_time": "2025-06-01T10:00:00Z",
            "arrival_time": "2025-06-01T12:00:00Z",
        }

        res = self.client.post(JOURNEY_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        journey = Journey.objects.get(id=res.data["id"])
        self.assertEqual(journey.train.id, payload["train"])
        self.assertEqual(journey.route.id, payload["route"])

    def test_journey_invalid_time(self):
        train = sample_train()
        route = sample_route()

        payload = {
            "train": train.id,
            "route": route.id,
            "departure_time": "2025-06-01T14:00:00Z",
            "arrival_time": "2025-06-01T10:00:00Z",
        }

        res = self.client.post(JOURNEY_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_time", res.data)


# ----------------------- JOURNEY FILTER TESTS -----------------------

class JourneyFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

        # Stations
        self.s1 = Station.objects.create(name="Kyiv", latitude=0, longitude=0)
        self.s2 = Station.objects.create(name="Lviv", latitude=1, longitude=1)
        self.s3 = Station.objects.create(name="Odesa", latitude=2, longitude=2)

        # Routes
        self.r1 = Route.objects.create(
            source=self.s1, destination=self.s2, distance=500
        )
        self.r2 = Route.objects.create(
            source=self.s2, destination=self.s3, distance=700
        )

        # Train
        self.train = sample_train()

        # Journeys
        self.j1 = Journey.objects.create(
            route=self.r1,
            train=self.train,
            departure_time="2025-06-01T10:00:00Z",
            arrival_time="2025-06-01T15:00:00Z",
        )
        self.j2 = Journey.objects.create(
            route=self.r2,
            train=self.train,
            departure_time="2025-06-10T08:00:00Z",
            arrival_time="2025-06-10T14:00:00Z",
        )

    def test_filter_by_source(self):
        res = self.client.get(JOURNEY_URL, {"source": "kyiv"})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.j1.id)

    def test_filter_by_destination(self):
        res = self.client.get(JOURNEY_URL, {"dest": "odesa"})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.j2.id)

    def test_filter_by_departure_range(self):
        res = self.client.get(
            JOURNEY_URL,
            {"depart_from": "2025-06-05", "depart_to": "2025-06-15"},
        )
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.j2.id)

    def test_filter_by_arrival_range(self):
        res = self.client.get(
            JOURNEY_URL,
            {"arrive_from": "2025-06-01", "arrive_to": "2025-06-02"},
        )
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.j1.id)

    def test_filter_by_tickets_left(self):
        # Create order and ticket for j1
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(
            order=order,
            journey=self.j1,
            cargo=1,
            seat=1,
        )

        min_free = (
            self.train.cargo_num * self.train.places_in_cargo - 1
        )

        res = self.client.get(JOURNEY_URL, {"tickets_left": min_free})
        returned_ids = {item["id"] for item in res.data}

        self.assertIn(self.j1.id, returned_ids)
        self.assertIn(self.j2.id, returned_ids)

        # Now require more than j1 has left
        res = self.client.get(JOURNEY_URL, {"tickets_left": min_free + 1})
        returned_ids = {item["id"] for item in res.data}

        self.assertNotIn(self.j1.id, returned_ids)
        self.assertIn(self.j2.id, returned_ids)
