from django.urls import path
from .views import PongLoginView, PongRegisterView, PongUserView, VerifyOTPView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', PongLoginView.as_view(), name='login'),
    path('register/', PongRegisterView.as_view(), name='register'),
    path('<int:pk>/', PongUserView.as_view(), name='user_detail'),
    path('token_refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
]