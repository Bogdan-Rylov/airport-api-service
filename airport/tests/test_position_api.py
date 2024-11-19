from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Position
from airport.serializers import PositionSerializer


User = get_user_model()

POSITIONS_URL = reverse("airport:position-list")


def sample_position(**additional_kwargs) -> Position:
    default_kwargs = {
        "name": "Test Pilot"
    }
    default_kwargs.update(additional_kwargs)

    return Position.objects.create(**default_kwargs)


class UnauthenticatedPositionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_position_list_unauthorized(self):
        response = self.client.get(POSITIONS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPositionTests(TestCase):
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

    def test_position_list_forbidden(self):
        response = self.client.get(POSITIONS_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPositionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        sample_position()
        sample_position(name="Co-Pilot")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_position_list(self):
        response = self.client.get(POSITIONS_URL)

        positions = Position.objects.all()
        serializer = PositionSerializer(positions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_position_create(self):
        payload = {"name": "Flight Attendant"}

        response = self.client.post(POSITIONS_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        position = Position.objects.get(id=response.data["id"])
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(position, variable_name)
            )
