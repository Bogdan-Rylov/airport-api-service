from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight, Airport, AirplaneType, Airplane, Route
from airport.serializers import FlightListSerializer
from airport.tests.test_crew_member_api import sample_crew_member


User = get_user_model()

FLIGHTS_URL = reverse("airport:flight-list")


def sample_flight(**additional_kwargs) -> Flight:
    default_kwargs = {
        "route": None,
        "airplane": None,
        "departure_time": datetime.now() + timedelta(hours=1),
        "arrival_time": datetime.now() + timedelta(hours=3)
    }
    default_kwargs.update(additional_kwargs)

    return Flight.objects.create(**default_kwargs)


def initialize_test_data() -> dict:
    airplane_type_1 = AirplaneType.objects.create(
        model="A320",
        manufacturer="Airbus",
        rows=30,
        seats_in_row=6,
    )
    airplane_type_2 = AirplaneType.objects.create(
        model="737",
        manufacturer="Boeing",
        rows=35,
        seats_in_row=6,
    )
    airplane_1 = Airplane.objects.create(
        type=airplane_type_1,
        serial_number="B737-001"
    )
    airplane_2 = Airplane.objects.create(
        type=airplane_type_2,
        serial_number="B737-002"
    )
    airport_1 = Airport.objects.create(
        name="John F. Kennedy International Airport",
        city="New York",
        country="USA",
        iata_code="JFK"
    )
    airport_2 = Airport.objects.create(
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="USA",
        iata_code="LAX"
    )
    route_1 = Route.objects.create(
        source=airport_1,
        destination=airport_2
    )
    route_2 = Route.objects.create(
        source=airport_2,
        destination=airport_1
    )
    crew_member = sample_crew_member()

    return {
        "airplane_type_1": airplane_type_1,
        "airplane_type_2": airplane_type_2,
        "airplane_1": airplane_1,
        "airplane_2": airplane_2,
        "airport_1": airport_1,
        "airport_2": airport_2,
        "route_1": route_1,
        "route_2": route_2,
        "crew_member": crew_member
    }


class UnauthenticatedFlightTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = initialize_test_data()

        flight_1 = sample_flight(
            route=data["route_1"],
            airplane=data["airplane_1"]
        )
        flight_1.crew.add(data["crew_member"])

        flight_2 = sample_flight(
            route=data["route_2"],
            airplane=data["airplane_2"]
        )
        flight_2.crew.add(data["crew_member"])

        data["flight_1"] = flight_1
        data["flight_2"] = flight_2

        cls.test_data = data

    def setUp(self):
        self.client = APIClient()

    def test_flight_list(self):
        response = self.client.get(FLIGHTS_URL)

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__type__rows")
                * F("airplane__type__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_create_forbidden(self):
        payload = {
            "route": self.test_data["route_1"].id,
            "airplane": self.test_data["airplane_2"].id,
            "departure_time": datetime.now() + timedelta(hours=1),
            "arrival_time": datetime.now() + timedelta(hours=3),
            "crew": self.test_data["crew_member"].id
        }

        response = self.client.post(FLIGHTS_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="test12345",
            is_staff=False
        )
        data = initialize_test_data()

        flight_1 = sample_flight(
            route=data["route_1"],
            airplane=data["airplane_1"]
        )
        flight_1.crew.add(data["crew_member"])

        flight_2 = sample_flight(
            route=data["route_2"],
            airplane=data["airplane_2"]
        )
        flight_2.crew.add(data["crew_member"])

        data["flight_1"] = flight_1
        data["flight_2"] = flight_2

        cls.test_data = data

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_flight_list(self):
        response = self.client.get(FLIGHTS_URL)

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__type__rows")
                * F("airplane__type__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_create_forbidden(self):
        payload = {
            "route": self.test_data["route_1"].id,
            "airplane": self.test_data["airplane_2"].id,
            "departure_time": datetime.now() + timedelta(hours=1),
            "arrival_time": datetime.now() + timedelta(hours=3),
            "crew": self.test_data["crew_member"].id
        }

        response = self.client.post(FLIGHTS_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        data = initialize_test_data()

        flight_1 = sample_flight(
            route=data["route_1"],
            airplane=data["airplane_1"]
        )
        flight_1.crew.add(data["crew_member"])

        flight_2 = sample_flight(
            route=data["route_2"],
            airplane=data["airplane_2"]
        )
        flight_2.crew.add(data["crew_member"])

        data["flight_1"] = flight_1
        data["flight_2"] = flight_2

        cls.test_data = data

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_flight_list(self):
        response = self.client.get(FLIGHTS_URL)

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__type__rows")
                * F("airplane__type__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_create(self):
        payload = {
            "route": self.test_data["route_1"].id,
            "airplane": self.test_data["airplane_2"].id,
            "departure_time": datetime.now(timezone.utc) + timedelta(hours=1),
            "arrival_time": datetime.now(timezone.utc) + timedelta(hours=3),
            "crew": [self.test_data["crew_member"].id, ]
        }

        response = self.client.post(FLIGHTS_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=response.data["id"])

        self.assertEqual(payload["route"], flight.route.id)
        self.assertEqual(payload["airplane"], flight.airplane.id)
        self.assertEqual(payload["departure_time"], flight.departure_time)
        self.assertEqual(payload["arrival_time"], flight.arrival_time)
        for crew in flight.crew.all():
            self.assertIn(crew.id, payload["crew"])
