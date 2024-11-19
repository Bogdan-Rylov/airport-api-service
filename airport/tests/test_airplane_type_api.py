from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeListSerializer


User = get_user_model()

AIRPLANE_TYPES_URL = reverse("airport:airplanetype-list")


def sample_airplane_type(**additional_kwargs) -> AirplaneType:
    default_kwargs = {
        "model": None,
        "manufacturer": "test",
        "rows": 30,
        "seats_in_row": 6,
    }
    default_kwargs.update(additional_kwargs)

    return AirplaneType.objects.create(**default_kwargs)


class UnauthenticatedAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_airplane_type_list_unauthorized(self):
        response = self.client.get(AIRPLANE_TYPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="test12345",
            is_staff=False
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_airplane_type_list_forbidden(self):
        response = self.client.get(AIRPLANE_TYPES_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        sample_airplane_type(model="Airbus", manufacturer="A320")
        sample_airplane_type(model="Boeing", manufacturer="737 Max")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_airplane_type_list(self):
        response = self.client.get(AIRPLANE_TYPES_URL)

        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeListSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_create(self):
        payload = {
            "model": "190",
            "manufacturer": "Embraer",
            "rows": 25,
            "seats_in_row": 4,
        }

        response = self.client.post(AIRPLANE_TYPES_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane_type = AirplaneType.objects.get(id=response.data["id"])
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(airplane_type, variable_name)
            )
