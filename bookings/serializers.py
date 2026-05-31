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
        date = self.context.get('date')
        if not date:
            return None
        
        time_start = self.context.get('time_start')
        time_end = self.context.get('time_end')
        
        booking_filter = {
            'booking_date': date,
            'status': 'active',
        }

        if time_start and time_end:
            if time_end <= time_start:
                raise serializers.ValidationError(
                    {"time_end": "Час закінчення повинен бути пізніше часу початку."}
                )
            booking_filter['time_start__lt'] = time_end
            booking_filter['time_end__gt'] = time_start

        return not obj.bookings.filter(
            **booking_filter,
        ).exists()


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = ['id', 'user', 'workspace', 'booking_date', 'status', 'created_at', 'updated_at', 'time_start', 'time_end']
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']
        extra_kwargs = {
            'time_start': {'required': True},
            'time_end': {'required': True},
        }

    def validate(self, data):

        user = self.context['request'].user

        if self.instance:
            if not user.is_staff:
                forbidden_fields = ['workspace', 'booking_date', 'time_start', 'time_end']
                for field in forbidden_fields:
                    if field in data and data[field] != getattr(self.instance, field):
                        raise serializers.ValidationError(
                            {field: "Звичайний користувач не може змінювати параметри вже створеного бронюванняю"}
                        )
                if data.get('status') == 'active' and self.instance.status == 'cancelled':
                    raise serializers.ValidationError(
                        {"status": "Не можна повторно активувати скасоване бронювання."}
                    )
                
            if data.get('status') == 'cancelled':
                return data
            
        
        workspace = data.get('workspace') or getattr(self.instance, 'workspace', None)
        booking_date = data.get('booking_date') or getattr(self.instance, 'booking_date', None)

        time_start = data.get('time_start') or getattr(self.instance, 'time_start', None)
        time_end = data.get('time_end') or getattr(self.instance, 'time_end', None)

        if not workspace or not booking_date or not time_start or not time_end:
            return data

        if time_end <= time_start:
            raise serializers.ValidationError(
                {"time_end": "Час закінчення повинен бути пізніше часу початку."}
            )

        qs = Booking.objects.filter(
            workspace=workspace,
            booking_date=booking_date,
            status='active',
            time_start__lt=time_end,
            time_end__gt=time_start,
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Цей стіл вже зайнятий на цю дату.")

        return data