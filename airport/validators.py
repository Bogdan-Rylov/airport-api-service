from datetime import date

import regex as re
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_normalized_string(value: str) -> None:
    pattern = r"^[\p{L}\s-']+$"
    if not re.match(pattern, value):
        raise ValidationError(
            "The string must contain only letters, spaces, hyphens, "
            "and apostrophes."
        )

    chars = (" ", "-", "'")
    if value.startswith(chars) or value.endswith(chars):
        raise ValidationError(
            "The string must not start or end with special characters"
        )


def validate_positive_number(value: int | float) -> None:
    if value < 0:
        raise ValidationError(
            "Value cannot be negative.",
            params={"value": value},
        )


def validate_minimum_age_from_birthdate(
    value: date,
    min_age: int = 18
) -> None:
    today = date.today()
    age = (today - value).days // 365
    if age < min_age:
        raise ValidationError(
            f"Age must be at least {min_age} years.",
            params={"age": age},
        )


def validate_date_not_in_future(value: date) -> None:
    if value > timezone.now().date():
        raise ValidationError(
            "Date cannot be in the future.",
            params={"value": value},
        )


def validate_iata_code(value):
    pattern = r"^[A-Z]{3}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "IATA code should be 3 uppercase letters.",
            params={"value": value}
        )
