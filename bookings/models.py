from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Room(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['floor', 'name']

    def __str__(self):
        return f"{self.name} (поверх {self.floor})"
    

class Workspace(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='workspaces',
    )
    number = models.CharField(max_length=20)
    has_monitor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room', 'number']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'number'],
                name='unique_workspace_number_per_room'
            )
        ]
    
    def __str__(self):
        return f"Стіл {self.number} ({self.room.name})"
    

class Booking(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активне'),
        (STATUS_CANCELLED, 'Скасоване'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    booking_date = models.DateField()
    time_start = models.TimeField(default='09:00')
    time_end = models.TimeField(default='17:00')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date', 'time_start']
        indexes = [
            models.Index(fields=['workspace', 'booking_date', 'status']),
            models.Index(fields=['user', 'booking_date']),
        ]

    def __str__(self):
        return (
            f"{self.user} -> Стіл {self.workspace.number} "
            f"({self.booking_date} {self.time_start}-{self.time_end})"
        )
    
    def clean(self):
        if self.booking_date and self.booking_date < timezone.now().date():
            raise ValidationError('Не можна створити бронювання в минулому.')

        if self.time_end <= self.time_start:
            raise ValidationError('Час закінчення повинен бути пізніше часу початку.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)