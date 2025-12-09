from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class Station(models.Model):
    name = models.CharField(max_length=128)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class TrainType(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=128)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="departures"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="arrivals"
    )
    distance = models.PositiveIntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "Source and destination stations cannot be the same."
            )

    def __str__(self):
        return f"{self.source} → {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    crew = models.ManyToManyField(
        Crew,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} ({self.departure_time:%Y-%m-%d %H:%M})"

    class Meta:
        ordering = ("departure_time",)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user}"

    class Meta:
        ordering = ("-created_at",)


class Ticket(models.Model):
    cargo = models.PositiveIntegerField(default=0)
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for (attr_value, attr_name, train_attr_name) in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo")
        ]:
            attr_count = getattr(train, train_attr_name)
            if not 1 <= attr_value <= attr_count:
                raise error_to_raise(
                    {
                        train_attr_name: f"{train_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {attr_count})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError
        )

    def save(
        self,
        *,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return f"Ticket #{self.id} - Seat {self.seat} (Journey {self.journey_id})"

    class Meta:
        unique_together = ("journey", "cargo", "seat")
