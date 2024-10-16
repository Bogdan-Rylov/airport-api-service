from datetime import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
    FlightSerializer,
    OrderSerializer,
    OrderListSerializer,
    FlightListSerializer
)


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    # permission_classes = (IsAdmin,)

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

    # permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewMemberListSerializer

        if self.action == "retrieve":
            return CrewMemberRetrieveSerializer

        return CrewMemberSerializer

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

    # permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneTypeListSerializer

        return AirplaneTypeSerializer

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
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        return AirplaneSerializer

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
        .prefetch_related("crew__position")
    )
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightSerializer

        return FlightSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Get flights with filters"""
        route = self.request.query_params.get("route")
        airplane_types = self.request.query_params.get("airplane-types")
        airplanes = self.request.query_params.get("airplanes")
        departure_time_from = self.request.query_params.get(
            "departure-time-from"
        )
        departure_time_to = self.request.query_params.get("departure-time-to")
        arrival_time_from = self.request.query_params.get("arrival-time-from")
        arrival_time_to = self.request.query_params.get("arrival-time-to")

        queryset = self.queryset

        if route:
            try:
                route_id = int(route)
                queryset = queryset.filter(route__id=route_id)
            except ValueError:
                return Response(
                    {"error": "Invalid route ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if airplane_types:
            try:
                airplane_types_ids = self._params_to_ints(airplane_types)
                queryset = queryset.filter(
                    airplane__type__id__in=airplane_types_ids
                )
            except ValueError:
                return Response(
                    {"error": "Invalid airplane type ID(s)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if airplanes:
            try:
                airplanes_ids = self._params_to_ints(airplanes)
                queryset = queryset.filter(airplane__id__in=airplanes_ids)
            except ValueError:
                return Response(
                    {"error": "Invalid airplane ID(s)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if departure_time_from:
            try:
                departure_time_from_dt = datetime.fromisoformat(
                    departure_time_from
                )
                queryset = queryset.filter(
                    departure_time__gte=departure_time_from_dt
                )
            except ValueError:
                return Response(
                    {"error": "Invalid departure time from format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if departure_time_to:
            try:
                departure_time_to_dt = datetime.fromisoformat(
                    departure_time_to
                )
                queryset = queryset.filter(
                    departure_time__lte=departure_time_to_dt
                )
            except ValueError:
                return Response(
                    {"error": "Invalid departure time to format."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if arrival_time_from:
            try:
                arrival_time_from_dt = datetime.fromisoformat(
                    arrival_time_from
                )
                queryset = queryset.filter(
                    arrival_time__gte=arrival_time_from_dt
                )
            except ValueError:
                return Response(
                    {"error": "Invalid 'arrival time from' format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if arrival_time_to:
            try:
                arrival_time_to_dt = datetime.fromisoformat(arrival_time_to)
                queryset = queryset.filter(
                    arrival_time__lte=arrival_time_to_dt
                )
            except ValueError:
                return Response(
                    {"error": "Invalid arrival time to format."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return queryset.distinct()

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
                description="Filter by airplane type IDs (ex. ?airplane-types=1,2)"
            ),
            OpenApiParameter(
                name="airplanes",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by airplane IDs (ex. ?airplanes=3,4)"
            ),
            OpenApiParameter(
                name="departure_time_from",
                type={"type": "string", "format": "date-time"},
                description="Filter by departure time from (ex. ?departure_time_from=2024-10-15T10:00:00)"
            ),
            OpenApiParameter(
                name="departure_time_to",
                type={"type": "string", "format": "date-time"},
                description="Filter by departure time to (ex. ?departure_time_to=2024-10-15T12:00:00)"
            ),
            OpenApiParameter(
                name="arrival_time_from",
                type={"type": "string", "format": "date-time"},
                description="Filter by arrival time from (ex. ?arrival_time_from=2024-10-15T10:00:00)"
            ),
            OpenApiParameter(
                name="arrival_time_to",
                type={"type": "string", "format": "date-time"},
                description="Filter by arrival time to (ex. ?arrival_time_to=2024-10-15T12:00:00)"
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
    page_size = 10
    max_page_size = 100


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
