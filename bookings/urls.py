from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, BookingViewSet, register, login_view, home, test_ui

router = DefaultRouter()
router.register('workspaces', WorkspaceViewSet)
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', home),
    path('ui/', test_ui, name='test-ui'),
    path('api/v1/', include(router.urls)), 
    path('api/', include(router.urls)),       
    path('api/auth/register/', register),
    path('api/auth/login/', login_view),
    
]