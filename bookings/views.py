from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Workspace, Booking
from .serializers import WorkspaceSerializer, BookingSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


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
                'username': {'type': 'string'},
                'password': {'type': 'string'},
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
            value={'username': 'testuser', 'password': 'testpass123'},
            request_only=True,
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Користувач вже існує'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['auth'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
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
            'Register example',
            value={'username': 'testuser', 'password': 'testpass123'},
            request_only=True,
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Невірний логін або пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)


class WorkspaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['has_monitor', 'room']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date')
        return context


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=None,
        responses={
            200: {'type': 'object', 'properties': {'status': {'type': 'string'}}},
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        },
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == 'cancelled':
            return Response(
                {'error': 'Бронування вже скасовано.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'Бронювання скасовано.'})