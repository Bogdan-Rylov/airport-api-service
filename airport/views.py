from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from airport.filters import FlightFilterBackend
from airport.models import (
    Position,
    CrewMember,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order
)
from airport.permissions import IsAdmin
from airport.serializers import (
    PositionSerializer,
    CrewMemberSerializer,
    CrewMemberListSerializer,
    CrewMemberRetrieveSerializer,
    AirplaneTypeSerializer,
    AirplaneTypeListSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
)


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAdmin,)

    def list(self, request, *args, **kwargs):
        """Get list of all positions."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new position."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve position."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update position."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete position."""
        return super().destroy(request, *args, **kwargs)


class CrewMemberViewSet(ModelViewSet):
    queryset = CrewMember.objects.select_related("position")
    serializer_class = CrewMemberSerializer
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return CrewMemberListSerializer
        elif self.action == "retrieve":
            return CrewMemberRetrieveSerializer

        return default_serializer

    def list(self, request, *args, **kwargs):
        """Get list of all crew members."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new crew member."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get crew member."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update crew member."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete crew member."""
        return super().destroy(request, *args, **kwargs)


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return AirplaneTypeListSerializer

        return default_serializer

    def list(self, request, *args, **kwargs):
        """Get list of all airplane types."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new airplane type."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get airplane type."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update airplane type."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete airplane type."""
        return super().destroy(request, *args, **kwargs)


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related("type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer

        return default_serializer

    def list(self, request, *args, **kwargs):
        """Get list of all airplanes."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new airplane."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get airplane."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update airplane."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete airplane."""
        return super().destroy(request, *args, **kwargs)


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def list(self, request, *args, **kwargs):
        """Get list of all airports."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new airport."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get airport."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update airport."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete airport."""
        return super().destroy(request, *args, **kwargs)


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer

        return default_serializer

    def list(self, request, *args, **kwargs):
        """Get list of all routes."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new route."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get route."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update route."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete route."""
        return super().destroy(request, *args, **kwargs)


class FlightViewSet(ModelViewSet):
    queryset = (
        Flight.objects
        .select_related(
            "route__source",
            "route__destination",
            "airplane__type"
        )
    )
    filter_backends = [FlightFilterBackend]
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer

        return default_serializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = self.queryset.filter(
                departure_time__gte=datetime.now()
            )

            queryset = queryset.annotate(
                tickets_available=(
                    F("airplane__type__rows")
                    * F("airplane__type__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related("crew__position")

        return queryset

    @extend_schema(
        description="Retrieve a list of flights.",
        parameters=[
            OpenApiParameter(
                name="route",
                type={"type": "number"},
                description="Filter by route ID (ex. ?route=1)"
            ),
            OpenApiParameter(
                name="airplane-types",
                type={"type": "array", "items": {"type": "number"}},
                description=(
                    "Filter by airplane type IDs (ex. ?airplane-types=1,2)"
                )
            ),
            OpenApiParameter(
                name="airplanes",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by airplane IDs (ex. ?airplanes=3,4)"
            ),
            OpenApiParameter(
                name="departure_time_from",
                type={"type": "string", "format": "date-time"},
                description=(
                    "Filter by departure time from "
                    "(ex. ?departure_time_from=2024-10-15T10:00:00)"
                )
            ),
            OpenApiParameter(
                name="departure_time_to",
                type={"type": "string", "format": "date-time"},
                description=(
                    "Filter by departure time to "
                    "(ex. ?departure_time_to=2024-10-15T12:00:00)"
                )
            ),
            OpenApiParameter(
                name="arrival_time_from",
                type={"type": "string", "format": "date-time"},
                description=(
                    "Filter by arrival time from "
                    "(ex. ?arrival_time_from=2024-10-15T10:00:00)"
                )
            ),
            OpenApiParameter(
                name="arrival_time_to",
                type={"type": "string", "format": "date-time"},
                description=(
                    "Filter by arrival time to "
                    "(ex. ?arrival_time_to=2024-10-15T12:00:00)"
                )
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Get list of all flights, optionally filtered by route, airplane types,
        airplanes, or departure/arrival time
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new flight."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Get flight."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update flight."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete flight."""
        return super().destroy(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 7
    max_page_size = 20


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__flight__route",
                "tickets__flight__airplane"
            )

        return queryset

    def get_serializer_class(self):
        default_serializer = self.serializer_class

        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer

        return default_serializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
