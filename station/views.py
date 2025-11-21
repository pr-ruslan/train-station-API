from rest_framework import viewsets, mixins, status

from station.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Order,
    Ticket,
)
from station.serializers import (
    CrewSerializer,
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    UserSerializer,
    OrderDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    TicketSerializer,
    TicketListSerializer
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = ()


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = ()


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = ()

