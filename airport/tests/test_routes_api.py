from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer


User = get_user_model()

ROUTES_URL = reverse("airport:route-list")


def sample_route(**additional_kwargs) -> Route:
    default_kwargs = {
        "source": None,
        "destination": None,
    }
    default_kwargs.update(additional_kwargs)

    return Route.objects.create(**default_kwargs)


def populate_test_db() -> None:
    ny_airport = Airport.objects.create(
        name="John F. Kennedy International Airport",
        city="New York",
        country="USA",
        iata_code="JFK"
    )
    la_airport = Airport.objects.create(
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="USA",
        iata_code="LAX"
    )
    ln_airport = Airport.objects.create(
        name="Heathrow Airport",
        city="London",
        country="UK",
        iata_code="LHR"
    )

    sample_route(
        source=ny_airport,
        destination=la_airport,
    )
    sample_route(
        source=la_airport,
        destination=ln_airport,
    )


class UnauthenticatedRouteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        populate_test_db()

    def setUp(self):
        self.client = APIClient()

    def test_route_list(self):
        response = self.client.get(ROUTES_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_create_forbidden(self):
        payload = {
            "source": 1,
            "destination": 3,
        }

        response = self.client.post(ROUTES_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteTests(TestCase):
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

    def test_route_list(self):
        response = self.client.get(ROUTES_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_create_forbidden(self):
        payload = {
            "source": 1,
            "destination": 3,
        }

        response = self.client.post(ROUTES_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTests(TestCase):
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

    def test_route_list(self):
        response = self.client.get(ROUTES_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_create(self):
        payload = {
            "source": 1,
            "destination": 3,
        }

        response = self.client.post(ROUTES_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(payload["source"], route.source.id)
        self.assertEqual(payload["destination"], route.destination.id)
