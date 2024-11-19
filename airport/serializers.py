from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Position,
    CrewMember,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order,
    Ticket
)


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ("id", "name", "description")


class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMember
        fields = (
            "id",
            "license_number",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "position",
            "hiring_date",
            "previous_experience",
            "total_experience"
        )


class CrewMemberListSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source="position.name", read_only=True)

    class Meta:
        model = CrewMember
        fields = ("id", "license_number", "full_name", "gender", "position")


class CrewMemberRetrieveSerializer(CrewMemberSerializer):
    position = PositionSerializer(read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "model",
            "manufacturer",
            "rows",
            "seats_in_row",
            "capacity"
        )


class AirplaneTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "model",
            "manufacturer",
            "capacity"
        )


class AirplaneSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Airplane.validate_airplane(
            attrs.get("manufacture_date"),
            attrs.get("operation_start_date"),
            attrs.get("last_maintenance_date"),
            ValidationError
        )

        return data

    class Meta:
        model = Airplane
        fields = (
            "id",
            "type",
            "name",
            "serial_number",
            "manufacture_date",
            "operation_start_date",
            "last_maintenance_date"
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    type = AirplaneTypeListSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "type",
            "name",
            "serial_number"
        )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    type = AirplaneTypeSerializer(read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "city", "country", "iata_code")


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Route.validate_route(
            attrs["source"],
            attrs["destination"],
            ValidationError
        )

        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class FlightSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Flight.validate_flight(
            attrs["departure_time"],
            attrs["arrival_time"],
            ValidationError
        )

        return data

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.CharField(source="route.info", read_only=True)
    airplane = serializers.CharField(source="airplane.info", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane.type,
            ValidationError
        )

        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = serializers.CharField(source="flight.display", read_only=True)


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )
    crew = CrewMemberListSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "taken_places",
            "crew",
            "departure_time",
            "arrival_time"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
