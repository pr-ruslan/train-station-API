from django.contrib import admin

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

admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(Journey)
