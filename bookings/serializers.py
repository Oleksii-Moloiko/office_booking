from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Room, Workspace, Booking


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model. Includes basic room info with timestamps."""
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'floor', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for Workspace model.
    
    Includes availability check for specific date if provided in context.
    Usage: Pass 'date' in serializer context to get is_available field.
    """
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['id', 'number', 'room', 'has_monitor', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    @extend_schema_field(serializers.BooleanField(allow_null=True))
    def get_is_available(self, obj):
        """
        Check if workspace is available on given date.
        
        Returns None if date not provided, True/False if available/booked.
        """
        date = self.context.get('date')
        if not date:
            return None
        return not obj.bookings.filter(
            booking_date=date,
            status='active'
        ).exists()


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    
    - user: read-only, automatically set to current user
    - workspace: required workspace ID
    - booking_date: required date in YYYY-MM-DD format
    - status: read-only, set to 'active' by default
    - created_at, updated_at: read-only timestamps
    
    Validation: Prevents overbooking (same workspace/date)
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = ['id', 'user', 'workspace', 'booking_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate booking data.
        
        - Check if workspace and date are not already booked
        - Return validation error if conflict found
        """
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