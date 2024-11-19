from django.urls import path, include
from rest_framework import routers

from airport.views import (
    PositionViewSet,
    CrewMemberViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet
)


app_name = "airport"

router = routers.DefaultRouter()
router.register("positions", PositionViewSet)
router.register("crew-members", CrewMemberViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]
