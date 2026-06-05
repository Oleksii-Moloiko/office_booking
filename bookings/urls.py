from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, BookingViewSet, register, login_view, home, test_ui
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

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
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]