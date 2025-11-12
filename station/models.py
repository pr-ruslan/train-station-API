from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=128)
    latitude = models.FloatField()
    longitude = models.CharField()


class Ticket(models.Model):
    cargo = models.IntegerField(default=0)
    seat = models.IntegerField()
    journey = models.ForeignKey(
        "Journey",
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return f"Ticket #{self.id} - Seat {self.seat} (Journey {self.journey_id})"