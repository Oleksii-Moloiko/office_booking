import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from .models import Workspace, Booking
from .serializers import WorkspaceSerializer, BookingSerializer
from .security import (
    PasswordValidator, EmailValidator, SecurityLogger, get_client_ip,
    InvalidPasswordException, InvalidEmailException, DuplicateUserException
)
from drf_spectacular.utils import extend_schema, OpenApiExample


logger = logging.getLogger('bookings')


@extend_schema(
    tags=['system'],
    responses={200: {'type': 'object'}},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response(
        {
            'message': 'Office Booking API працює.',
            'endpoints': {
                'api_root': '/api/',
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'admin': '/admin/',
            },
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=['auth'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Email адреса користувача'},
                'password': {'type': 'string', 'description': 'Пароль (мін 8 символів, має цифру та спецсимвол)'},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {'token': {'type': 'string'}},
        },
        400: {
            'type': 'object',
            'properties': {'error': {'type': 'string'}},
        },
    },
    examples=[
        OpenApiExample(
            'Register example',
            value={'username': 'user@example.com', 'password': 'SecurePass123!'},
            request_only=True,
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def register(request):
    """
    Register a new user with email and password.
    
    - Email must be valid format
    - Password must be at least 8 chars with digit and special character
    - Rate limited: 5 requests per hour per IP
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    ip_address = get_client_ip(request)
    
    try:
        # Validate email format
        is_valid_email, email_error = EmailValidator.validate(username)
        if not is_valid_email:
            SecurityLogger.log_registration_attempt(username, False, email_error)
            return Response(
                {'error': email_error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            SecurityLogger.log_registration_attempt(username, False, 'User already exists')
            return Response(
                {'error': 'Користувач з цією email адресою вже зареєстрований'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password
        is_valid_password, password_error = PasswordValidator.validate(password)
        if not is_valid_password:
            SecurityLogger.log_registration_attempt(username, False, password_error)
            return Response(
                {'error': password_error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(username=username, password=password, email=username)
        token, _ = Token.objects.get_or_create(user=user)
        
        SecurityLogger.log_registration_attempt(username, True)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        SecurityLogger.log_auth_error('REGISTRATION', str(e), ip_address)
        return Response(
            {'error': 'Помилка під час реєстрації. Спробуйте пізніше.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['auth'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Email адреса'},
                'password': {'type': 'string', 'description': 'Пароль'},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {'token': {'type': 'string'}},
        },
        401: {
            'type': 'object',
            'properties': {'error': {'type': 'string'}},
        },
    },
    examples=[
        OpenApiExample(
            'Login example',
            value={'username': 'user@example.com', 'password': 'SecurePass123!'},
            request_only=True,
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def login_view(request):
    """
    Login user with email and password.
    
    - Returns authentication token on success
    - Rate limited: 5 requests per hour per IP
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    ip_address = get_client_ip(request)
    
    try:
        user = authenticate(username=username, password=password)
        if not user:
            SecurityLogger.log_login_attempt(username, False, ip_address)
            return Response(
                {'error': 'Невірна email адреса або пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, _ = Token.objects.get_or_create(user=user)
        SecurityLogger.log_login_attempt(username, True, ip_address)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
        
    except Exception as e:
        SecurityLogger.log_auth_error('LOGIN', str(e), ip_address)
        return Response(
            {'error': 'Помилка під час входу. Спробуйте пізніше.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class WorkspaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['has_monitor', 'room']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date')
        context['time_start'] = self.request.query_params.get('time_start')
        context['time_end'] = self.request.query_params.get('time_end')
        return context


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        
        user = self.request.user

        if user.is_staff:
            return Booking.objects.select_related('user', 'workspace').all()
        
        return Booking.objects.select_related('user', 'workspace').filter(user=user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        logger.info(
            'Booking created',
            extra={
                'user_id': self.request.user.id,
                'username': self.request.user.username,
                'workspace_id': booking.workspace.id,
                'booking_date': str(booking.booking_date),
            }
        )
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'cancelled':
            logger.warning(
                "Attempt to cancel already cancelled booking",
                extra={'booking_id': booking.id, 'user_id': request.user.id}
            )
            return Response(
                {'extra': 'Бронювання вже скасовано'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'cancelled'
        booking.save()
        logger.info(
            "Booking cancelled",
            extra={'booking_id': booking.id, 'user_id': request.user.id}
        )
        return Response({'status': 'Бронювання скасовано.'})