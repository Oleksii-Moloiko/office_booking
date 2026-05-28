from rest_framework import serializers
from .models import Room, Workspace, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class WorkspaceSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['id', 'number', 'room', 'has_monitor', 'is_available']

    def get_is_available(self, obj):
        date = self.context.get('date')
        if not date:
            return None
        return not obj.bookings.filter(
            booking_date=date,
            status='active'
        ).exists()


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = ['id', 'user', 'workspace', 'booking_date', 'status']

    def validate(self, data):
        workspace = data.get('workspace') or getattr(self.instance, 'workspace', None)
        booking_date = data.get('booking_date') or getattr(self.instance, 'booking_date', None)

        if not workspace or not booking_date:
            return data

        qs = Booking.objects.filter(
            workspace=workspace,
            booking_date=booking_date,
            status='active'
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Цей стіл вже зайнятий на цю дату.")

        return data