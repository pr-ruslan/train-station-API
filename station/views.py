from datetime import datetime
from django.db.models import Count, F, ExpressionWrapper, IntegerField
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.utils.dateparse import parse_date
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)


from station.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Order,
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
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List train types"),
    create=extend_schema(summary="Create train type"),
)
class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAuthenticated,)


@extend_schema_view(
    list=extend_schema(summary="List crews"),
    create=extend_schema(summary="Create crew"),
)
class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAuthenticated,)


@extend_schema_view(
    list=extend_schema(
        summary="List stations",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Search stations by partial name",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
    ),
    create=extend_schema(summary="Create a station"),
)
class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        name = self.request.query_params.get("name")
        queryset = Station.objects.all()
        if name:
           queryset = queryset.filter(name__icontains=name)
        return queryset


@extend_schema_view(
    list=extend_schema(
        summary="List routes",
    ),
    retrieve=extend_schema(
        summary="Retrieve route details",
    ),
    create=extend_schema(summary="Create a route"),
)
class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.select_related(
        "source", "destination"
    )
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List trains",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter trains by partial name",
                required=False,
                type=OpenApiTypes.STR,
            )
        ],
    ),
    retrieve=extend_schema(summary="Retrieve train details"),
    create=extend_schema(summary="Create a train"),
)
class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer

    def get_queryset(self):
        queryset = Train.objects.select_related(
        "train_type"
        )
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(summary="List orders for current user"),
    create=extend_schema(summary="Create an order"),
)
class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet
                  ):
    queryset = Order.objects.prefetch_related(
        "tickets",
        "tickets__journey",
        "tickets__journey__route__source",
        "tickets__journey__route__destination",
        "tickets__journey__train",
        "tickets__journey__train__train_type",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="List journeys with filters",
        parameters=[
            OpenApiParameter("tickets_left", OpenApiTypes.INT, False,
                             description="Filter by remaining tickets (>=)"),
            OpenApiParameter("source", OpenApiTypes.STR, False,
                             description="Filter by departure station name"),
            OpenApiParameter("dest", OpenApiTypes.STR, False,
                             description="Filter by destination station name"),
            OpenApiParameter("depart_from", OpenApiTypes.DATE, False,
                             description="Departure >= date (YYYY-MM-DD)"),
            OpenApiParameter("depart_to", OpenApiTypes.DATE, False,
                             description="Departure <= date (YYYY-MM-DD)"),
            OpenApiParameter("arrive_from", OpenApiTypes.DATE, False,
                             description="Arrival >= date"),
            OpenApiParameter("arrive_to", OpenApiTypes.DATE, False,
                             description="Arrival <= date"),
        ],
    ),
    retrieve=extend_schema(summary="Retrieve a journey"),
    create=extend_schema(summary="Create a journey"),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
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
        def get_date(date_string, end=False):
            date = parse_date(date_string)
            if not date:
                return None
            return datetime.combine(
                date,
                datetime.max.time() if end else datetime.min.time()
            )

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
                departure_time__gte=get_date(depart_from)
            )
        if depart_to:
            queryset = queryset.filter(
                departure_time__lte=get_date(depart_to)
            )
        if arrive_from:
            queryset = queryset.filter(
                arrival_time__gte=get_date(arrive_from)
            )
        if arrive_to:
            queryset = queryset.filter(
                arrival_time__lte=get_date(arrive_to)
            )

        return queryset
