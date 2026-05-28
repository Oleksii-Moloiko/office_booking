from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField()

    def __str__(self):
        return f"{self.name} (поверх {self.floor})"


class Workspace(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='workspace',
    )
    number = models.CharField(max_length=20)
    has_monitor = models.BooleanField(default=False)

    def __str__(self):
        return f"Стіл {self.number} ({self.room.name})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    booking_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    class Meta:
        unique_together = ['workspace', 'booking_date']

    def __str__(self):
        return f"{self.user} -> Стіл {self.workspace.number} ({self.booking_date})"