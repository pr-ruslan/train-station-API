from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Order,
    Ticket,
    User
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id",
                  "first_name",
                  "last_name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id",
                  "name",
                  "latitude",
                  "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name",)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class RouteDetailSerializer(RouteListSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id",
                  "created_at",
                  "user")


class OrderListSerializer(OrderSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="email"
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")


class OrderDetailSerializer(OrderListSerializer):
    user = UserSerializer(read_only=True)


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time"
        )


class JourneyListSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)


class JourneyDetailSerializer(JourneySerializer):
    route = RouteDetailSerializer(read_only=True)
    train = TrainDetailSerializer(read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id",
                  "seat",
                  "cargo",
                  "order",
                  "journey")

class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)
    order = OrderListSerializer(many=False, read_only=True)


