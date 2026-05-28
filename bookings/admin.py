from django.contrib import admin
from .models import Room, Workspace, Booking

admin.site.register(Room)
admin.site.register(Workspace)
admin.site.register(Booking)