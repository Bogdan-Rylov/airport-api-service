from datetime import date, datetime
from typing import Callable

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from airport.validators import (
    validate_minimum_age_from_birthdate,
    validate_positive_number,
    validate_normalized_string,
    validate_date_not_in_future,
    validate_iata_code,
)


User = get_user_model()


class Position(models.Model):
    name = models.CharField(
        max_length=127,
        unique=True,
        validators=[validate_normalized_string]
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    license_number = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(
        max_length=127,
        validators=[validate_normalized_string]
    )
    last_name = models.CharField(
        max_length=127,
        validators=[validate_normalized_string]
    )
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(
        validators=[validate_minimum_age_from_birthdate]
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        related_name="crew_members",
        blank=True,
        null=True
    )
    hiring_date = models.DateField(
        blank=True,
        null=True,
        validators=[validate_date_not_in_future]
    )
    previous_experience = models.IntegerField(
        blank=True,
        null=True,
        validators=[validate_positive_number]
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def total_experience(self) -> int:
        """Calculate total work experience."""
        total = self.previous_experience if self.previous_experience else 0

        if self.hiring_date:
            years_since_hiring = (date.today() - self.hiring_date).days // 365
            total += years_since_hiring

        return total

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    class Meta:
        verbose_name = "Crew Member"
        verbose_name_plural = "Crew Members"


class AirplaneType(models.Model):
    model = models.CharField(max_length=63)
    manufacturer = models.CharField(
        max_length=127,
        validators=[validate_normalized_string]
    )
    rows = models.IntegerField(validators=[validate_positive_number])
    seats_in_row = models.IntegerField(validators=[validate_positive_number])

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
    name = models.CharField(
        max_length=127,
        blank=True,
        null=True,
        validators=[validate_normalized_string]
    )
    serial_number = models.CharField(max_length=127, unique=True)
    manufacture_date = models.DateField(blank=True, null=True)
    operation_start_date = models.DateField(blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)

    @property
    def age(self) -> int:
        return timezone.now().year - self.manufacture_date.year

    @property
    def info(self) -> str:
        airplane_name = f" '{self.name}'" if self.name else ""
        return f"{self.type}{airplane_name} ({self.serial_number})"

    def __str__(self):
        return self.info

    @staticmethod
    def validate_airplane(
        manufacture_date: date | None,
        operation_start_date: date | None,
        last_maintenance_date: date | None,
        error_to_raise: Callable
    ) -> None:
        if operation_start_date and manufacture_date:
            if operation_start_date < manufacture_date:
                raise error_to_raise(
                    {
                        "operation_start_date": (
                            "Operation start date cannot be earlier than "
                            "manufacture date."
                        )
                    }
                )

        if last_maintenance_date and manufacture_date:
            if last_maintenance_date < manufacture_date:
                raise error_to_raise(
                    {
                        "last_maintenance": (
                            "Last maintenance date cannot be earlier than "
                            "manufacture date."
                        )
                    }
                )

        if operation_start_date and last_maintenance_date:
            if operation_start_date > last_maintenance_date:
                raise error_to_raise(
                    {
                        "operation_start_date": (
                            "Operation start date cannot be later than last "
                            "maintenance date."
                        )
                    }
                )

    def clean(self):
        Airplane.validate_airplane(
            self.manufacture_date,
            self.operation_start_date,
            self.last_maintenance_date,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["serial_number"]


class Airport(models.Model):
    name = models.CharField(
        max_length=127,
        validators=[validate_normalized_string]
    )
    city = models.CharField(
        max_length=63,
        validators=[validate_normalized_string]
    )
    country = models.CharField(
        max_length=63,
        validators=[validate_normalized_string]
    )
    iata_code = models.CharField(
        max_length=3,
        unique=True,
        validators=[validate_iata_code]
    )

    def __str__(self):
        return f"{self.name} ({self.iata_code} - {self.city}, {self.country})"

    class Meta:
        ordering = ["country", "city", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["country", "city", "name"],
                name="unique_country_city_name"
            )
        ]


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
    distance = models.IntegerField(
        blank=True,
        null=True,
        validators=[validate_positive_number]
    )

    @property
    def info(self) -> str:
        return (
            f"{self.source.city} ({self.source.iata_code}) -> "
            f"{self.destination.city} ({self.destination.iata_code})"
        )

    def __str__(self):
        return self.info

    @staticmethod
    def validate_route(
        source: Airport,
        destination: Airport,
        error_to_raise: Callable
    ) -> None:
        if source == destination:
            raise error_to_raise(
                {
                    "destination": f"Source and destination airports cannot "
                                   f"be the same."
                }
            )

    def clean(self):
        Route.validate_route(self.source, self.destination, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["source"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_source_destination"
            )
        ]


class Flight(models.Model):
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
    crew = models.ManyToManyField(CrewMember, related_name="flights")

    @property
    def display(self) -> str:
        return self.__str__()

    def __str__(self):
        return (
            f"{self.route}. Departure: {self.departure_time}. "
            f"Arrival: {self.arrival_time}"
        )

    @staticmethod
    def validate_flight(
        departure_time: datetime,
        arrival_time: datetime,
        error_to_raise: Callable
    ) -> None:
        if departure_time >= arrival_time:
            raise error_to_raise(
                {
                    "arrival_time": "Departure time must be earlier than "
                                    "arrival time."
                }
            )

    def clean(self):
        Flight.validate_flight(
            self.departure_time,
            self.arrival_time,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
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
    ) -> None:
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["row", "seat"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"],
                name="unique_flight_row_seat"
            )
        ]
