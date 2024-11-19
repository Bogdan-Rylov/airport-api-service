from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


User = get_user_model()


POSITIONS_URL = reverse("airport:position-list")
CREW_MEMBERS_URL = reverse("airport:crew-member-list")
AIRPLANE_TYPES_URL = reverse("airport:airplane-type-list")
AIRPLANES_URL = reverse("airport:airplane-list")
AIRPORTS_URL = reverse("airport:airport-list")
ROUTES_URL = reverse("airport:route-list")
FLIGHTS_URL = reverse("airport:flight-list")
ORDERS_URL = reverse("airport:order-list")


class PermissionTestCase(TestCase):
    def setUpTestData(self):
        self.admin_user = User.objects.create_user(
            email="admin@gmail.com",
            password="test12345",
            is_staff=True
        )
        self.user = User.objects.create_user(
            username="user@gmail.com",
            password="test12345",
            is_staff=False
        )

    def setUp(self):
        self.client = APIClient()

    def test_position_access_as_admin(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(POSITIONS_URL)

        self.assertEqual(response.status_code, 200)

    def test_position_access_as_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(POSITIONS_URL)

        self.assertEqual(response.status_code, 403)

    def test_position_access_as_unauthenticated_user(self):
        response = self.client.get(POSITIONS_URL)
        self.assertEqual(response.status_code, 403)



    def test_airport_access_as_unauthenticated_user(self):
        response = self.client.get("/api/airports/")
        self.assertEqual(response.status_code, 200)  # HTTP_200_OK

    def test_airport_create_as_admin(self):
        self.client.login(username="admin", password="admin123")
        data = {"name": "New Airport"}
        response = self.client.post("/api/airports/", data)
        self.assertEqual(response.status_code, 201)  # HTTP_201_CREATED

    def test_airport_create_as_regular_user(self):
        self.client.login(username="user", password="user123")
        data = {"name": "New Airport"}
        response = self.client.post("/api/airports/", data)
        self.assertEqual(response.status_code, 403)  # HTTP_403_FORBIDDEN

    # Тесты для IsAuthenticated permission
    def test_order_access_as_authenticated_user(self):
        self.client.login(username="user", password="user123")
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)  # HTTP_200_OK

    def test_order_access_as_anonymous(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 403)  # HTTP_403_FORBIDDEN
