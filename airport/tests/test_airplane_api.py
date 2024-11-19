from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer


User = get_user_model()

AIRPLANES_URL = reverse("airport:airplane-list")


def sample_airplane(**additional_kwargs) -> Airplane:
    default_kwargs = {
        "type": None,
        "serial_number": None,
    }
    default_kwargs.update(additional_kwargs)

    return Airplane.objects.create(**default_kwargs)


def populate_test_db() -> None:
    airplane_type = AirplaneType.objects.create(
        **{
            "model": "737",
            "manufacturer": "Boeing",
            "rows": 35,
            "seats_in_row": 6,
        }
    )
    sample_airplane(type=airplane_type, serial_number="B737-001")
    sample_airplane(type=airplane_type, serial_number="B737-002")


class UnauthenticatedAirplaneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        populate_test_db()

    def setUp(self):
        self.client = APIClient()

    def test_airplane_list(self):
        response = self.client.get(AIRPLANES_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_create_unauthorized(self):
        payload = {
            "type": 1,
            "serial_number": "B737-003",
        }

        response = self.client.post(AIRPLANES_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTests(TestCase):
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

    def test_airplane_list(self):
        response = self.client.get(AIRPLANES_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_create_forbidden(self):
        payload = {
            "type": 1,
            "serial_number": "B737-003",
        }
        response = self.client.post(AIRPLANES_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):
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

    def test_airplane_list(self):
        response = self.client.get(AIRPLANES_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_create(self):
        payload = {
            "type": 1,
            "serial_number": "B737-003",
        }

        response = self.client.post(AIRPLANES_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=response.data["id"])

        self.assertEqual(
            payload.pop("type"),
            getattr(airplane, "type").id
        )
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(airplane, variable_name)
            )
