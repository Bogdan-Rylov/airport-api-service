import logging
from datetime import datetime

from django.db.models import QuerySet
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.views import APIView


logger = logging.getLogger(__name__)


def _params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class FlightFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView
    ) -> QuerySet:
        route = request.query_params.get("route")
        airplane_types = request.query_params.get("airplane-types")
        airplanes = request.query_params.get("airplanes")

        departure_time_from = request.query_params.get("departure-time-from")
        departure_time_to = request.query_params.get("departure-time-to")
        arrival_time_from = request.query_params.get("arrival-time-from")
        arrival_time_to = request.query_params.get("arrival-time-to")

        if route:
            try:
                route_id = int(route)
                queryset = queryset.filter(route__id=route_id)
            except ValueError:
                logger.warning(f"Ignored invalid Route ID parameter: {route}")

        if airplane_types:
            try:
                airplane_types_ids = _params_to_ints(airplane_types)
                queryset = queryset.filter(
                    airplane__type__id__in=airplane_types_ids
                )
            except ValueError:
                logger.warning(
                    f"Ignored invalid Airplane Type ID(s) parameter: "
                    f"{airplane_types}"
                )

        if airplanes:
            try:
                airplanes_ids = _params_to_ints(airplanes)
                queryset = queryset.filter(airplane__id__in=airplanes_ids)
            except ValueError:
                logger.warning(
                    f"Ignored invalid Airplane ID(s) parameter: {airplanes}"
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
                logger.warning(
                    f"Ignored invalid Departure Time From parameter: "
                    f"{departure_time_from}"
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
                logger.warning(
                    f"Ignored invalid Departure Time To parameter: "
                    f"{departure_time_to}"
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
                logger.warning(
                    f"Ignored invalid Arrival Time From parameter: "
                    f"{arrival_time_from}"
                )

        if arrival_time_to:
            try:
                arrival_time_to_dt = datetime.fromisoformat(arrival_time_to)
                queryset = queryset.filter(
                    arrival_time__lte=arrival_time_to_dt
                )
            except ValueError:
                logger.warning(
                    f"Ignored invalid Arrival Time To parameter: "
                    f"{arrival_time_from}"
                )

        return queryset.distinct()
