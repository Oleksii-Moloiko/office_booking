from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, BookingViewSet, register, login_view

router = DefaultRouter()
router.register('workspaces', WorkspaceViewSet)
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/register/', register),
    path('api/auth/login/', login_view),

]