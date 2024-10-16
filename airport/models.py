from typing import Callable

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class CrewMember(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    license_number = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        related_name="crew_members",
        null=True
    )
    hiring_date = models.DateField(blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    class Meta:
        ordering = ["last_name"]


class AirplaneType(models.Model):
    model = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        ordering = ["manufacturer", "model"]
        constraints = [
            models.UniqueConstraint(
                fields=["model", "manufacturer"],
                name="unique_model_manufacturer"
            )
        ]


class Airplane(models.Model):
    type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacture_date = models.DateField(blank=True, null=True)
    operation_start_date = models.DateField(blank=True, null=True)
    last_maintenance = models.DateField(blank=True, null=True)

    @property
    def age(self) -> int:
        return timezone.now().year - self.manufacture_date.year

    @property
    def info(self) -> str:
        airplane_name = f" '{self.name}'" if self.name else ""
        return f"{self.type}{airplane_name} ({self.serial_number})"

    def __str__(self):
        return self.info

    class Meta:
        ordering = ["serial_number"]


class Airport(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    iata_code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return f"{self.name} ({self.city} - {self.country}) [{self.iata_code}]"

    class Meta:
        ordering = ["country", "city", "name"]


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.info

    @property
    def info(self) -> str:
        return (
            f"{self.source.city} ({self.source.iata_code}) -> "
            f"{self.destination.city} ({self.destination.iata_code})"
        )

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "Source and destination airports cannot be the same.")
        if self.distance is not None and self.distance < 0:
            raise ValidationError(
                "Distance cannot be negative."
            )

    class Meta:
        ordering = ["source"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_source_destination"
            )
        ]


class Flight(models.Model):
    crew = models.ManyToManyField(CrewMember, related_name="flights")
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.route}. Departure: {self.departure_time}. "
            f"Arrival: {self.arrival_time}"
        )

    def clean(self):
        if self.departure_time >= self.arrival_time:
            raise ValidationError(
                "Departure time must be earlier than arrival time.")

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    @staticmethod
    def validate_ticket(
        row: int,
        seat: int,
        airplane_type: AirplaneType,
        error_to_raise: Callable
    ):
        for ticket_attr_value, ticket_attr_name, airplane_type_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane_type, airplane_type_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number "
                                          f"must be in available range: "
                                          f"(1, {airplane_type_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane.type,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        return super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    class Meta:
        ordering = ["row", "seat"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"],
                name="unique_flight_row_seat"
            )
        ]
