from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportSerializer


User = get_user_model()

AIRPORTS_URL = reverse("airport:airport-list")


def sample_airport(**additional_kwargs) -> Airport:
    default_kwargs = {
        "name": None,
        "city": None,
        "country": None,
        "iata_code": None,
    }
    default_kwargs.update(additional_kwargs)

    return Airport.objects.create(**default_kwargs)


def populate_test_db() -> None:
    sample_airport(
        name="John F. Kennedy International Airport",
        city="New York",
        country="USA",
        iata_code="JFK"
    )
    sample_airport(
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="USA",
        iata_code="LAX"
    )


class UnauthenticatedAirportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        populate_test_db()

    def setUp(self):
        self.client = APIClient()

    def test_airport_list(self):
        response = self.client.get(AIRPORTS_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_create_forbidden(self):
        payload = {
            "name": "Heathrow Airport",
            "city": "London",
            "country": "UK",
            "iata_code": "LHR",
        }

        response = self.client.post(AIRPORTS_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="test12345",
            is_staff=False
        )
        populate_test_db()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        response = self.client.get(AIRPORTS_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_create_forbidden(self):
        payload = {
            "name": "Heathrow Airport",
            "city": "London",
            "country": "UK",
            "iata_code": "LHR",
        }

        response = self.client.post(AIRPORTS_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        populate_test_db()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_airport_list(self):
        response = self.client.get(AIRPORTS_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_create(self):
        payload = {
            "name": "Heathrow Airport",
            "city": "London",
            "country": "UK",
            "iata_code": "LHR",
        }

        response = self.client.post(AIRPORTS_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(id=response.data["id"])
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(airport, variable_name)
            )
