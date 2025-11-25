from datetime import datetime
from django.db.models import Count, F, ExpressionWrapper, IntegerField
from rest_framework import viewsets, mixins

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
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = ()

    def get_queryset(self):
        name = self.request.query_params.get("name")
        queryset = self.queryset
        if name:
           queryset = queryset.filter(name__icontains=name)
        return queryset

class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.prefetch_related(
        "source", "destination"
    )
    permission_classes = ()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Train.objects.prefetch_related(
        "train_type"
    )
    permission_classes = ()

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects
        .select_related(
            "route",
            "route__source",
            "route__destination",
            "train",
            "train__train_type"
        )
        .prefetch_related("tickets")
    )

    @staticmethod
    def _params_to_ids(ids_string):
        return [int(str_id) for str_id in ids_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer

    def get_queryset(self):
        def parse_date(date_string):
            return datetime.strptime(date_string, "%Y-%m-%d")

        queryset = self.queryset.annotate(
            total_seats=ExpressionWrapper(
                F("train__cargo_num") *
                F("train__places_in_cargo"),
                output_field=IntegerField()
            ),
            tickets_sold=Count("tickets"),
            free_seats=ExpressionWrapper(
                F("train__cargo_num") *
                F("train__places_in_cargo") -
                Count("tickets"),
                output_field=IntegerField()
            )
        )

        tickets_left = self.request.query_params.get("tickets_left")
        source = self.request.query_params.get("source")
        dest = self.request.query_params.get("dest")
        depart_from = self.request.query_params.get("depart_from")
        depart_to = self.request.query_params.get("depart_to")
        arrive_from = self.request.query_params.get("arrive_from")
        arrive_to = self.request.query_params.get("arrive_to")

        if tickets_left:
            queryset = queryset.filter(free_seats__gte=int(tickets_left))
        if source:
            queryset = queryset.filter(
                route__source__name__icontains=source
            )
        if dest:
            queryset = queryset.filter(
                route__destination__name__icontains=dest
            )
        if depart_from:
            queryset = queryset.filter(
                departure_time__gte=parse_date(depart_from)
            )
        if depart_to:
            queryset = queryset.filter(
                departure_time__lte=parse_date(depart_to)
            )
        if arrive_from:
            queryset = queryset.filter(
                arrival_time__gte=parse_date(arrive_from)
            )
        if arrive_to:
            queryset = queryset.filter(
                arrival_time__lte=parse_date(arrive_to)
            )

        return queryset
