from rest_framework import routers
from django.urls import path, include

from station.views import (
    TrainTypeViewSet,
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    OrderViewSet,
    JourneyViewSet
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("crew", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("orders", OrderViewSet)
router.register("journey", JourneyViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "station"