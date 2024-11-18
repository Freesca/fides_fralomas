from django.urls import path
from .views import PongLoginView, PongRegisterView, PongUserView, VerifyOTPView, PongProfileView, PongUserListView, PongRefreshTokenView, PongLogoutView

app_name = 'user_mgmt_api'

urlpatterns = [
    path('login/', PongLoginView.as_view(), name='login'),
    path('logout/', PongLogoutView.as_view(), name='logout'),
    path('register/', PongRegisterView.as_view(), name='register'),
    path('profile/', PongProfileView.as_view(), name='profile'),
    path('user_list/', PongUserListView.as_view(), name='user_list'),
    path('user/<str:username>/', PongUserView.as_view(), name='user_detail'),
    path('token_refresh/', PongRefreshTokenView.as_view(), name='token_refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
]