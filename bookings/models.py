from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Room(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    time_start = models.TimeField(default='09:00') 
    time_end = models.TimeField(default='17:00')

    class Meta:
        pass

    def __str__(self):
        return f"{self.user} -> Стіл {self.workspace.number} ({self.booking_date} {self.time_start}-{self.time_end})"
    
    def clean(self):
        """Валідація: час закінчення повинен бути пізніше часу початку."""
        if self.time_end <= self.time_start:
            raise ValidationError('Час закінчення повинен бути пізніше часу початку.')

    def save(self, *args, **kwargs):
        """Викликаємо full_clean() перед збереженням."""
        self.full_clean()
        super().save(*args, **kwargs)

