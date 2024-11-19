from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import CrewMember
from airport.serializers import CrewMemberListSerializer


User = get_user_model()

CREW_MEMBERS_URL = reverse("airport:crewmember-list")


def sample_crew_member(**additional_kwargs) -> CrewMember:
    default_kwargs = {
        "license_number": "A000001",
        "first_name": "John",
        "last_name": "Doe",
        "gender": CrewMember.Gender.MALE,
        "date_of_birth": date.today().replace(year=date.today().year - 30),
    }
    default_kwargs.update(additional_kwargs)

    return CrewMember.objects.create(**default_kwargs)


class UnauthenticatedCrewMemberTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crew_member_list_unauthorized(self):
        response = self.client.get(CREW_MEMBERS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewMemberTests(TestCase):
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

    def test_crew_member_list_forbidden(self):
        response = self.client.get(CREW_MEMBERS_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewMemberTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        sample_crew_member()
        sample_crew_member(
            license_number="A000002",
            first_name="Michael",
            last_name="Johnson"
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_crew_member_list(self):
        response = self.client.get(CREW_MEMBERS_URL)

        crew_members = CrewMember.objects.all()
        serializer = CrewMemberListSerializer(crew_members, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_member_create(self):
        payload = {
            "license_number": "B000003",
            "first_name": "Emily",
            "last_name": "Smith",
            "gender": CrewMember.Gender.FEMALE,
            "date_of_birth": date.today().replace(year=date.today().year - 25),
        }

        response = self.client.post(CREW_MEMBERS_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        crew_member = CrewMember.objects.get(id=response.data["id"])
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(crew_member, variable_name)
            )
