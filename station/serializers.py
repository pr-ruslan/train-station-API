from rest_framework import serializers

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


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


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
        many=True,
        read_only=True,
        slug_field="name",
    )



class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=True, read_only=True)


