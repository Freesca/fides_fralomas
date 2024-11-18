from django.urls import path
from .views import PongPrivatePasswordMatchView

app_name = 'mtcmkg_api'

urlpatterns = [
    path('private-password/', PongPrivatePasswordMatchView.as_view(), name='private_password'),
]