from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class PongUser(AbstractUser):
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    trophies = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


# Create your models here.
