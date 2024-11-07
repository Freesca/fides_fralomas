from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PongRegisterSerializer, VerifyOTPSerializer
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

class PongRegisterView(APIView):
    def post(self, request):
        serializer = PongRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user.otp_secret = pyotp.random_base32()
        user.save()
        totp = pyotp.TOTP(user.otp_secret)
        otp_code = totp.now()

        send_mail(
            subject='OTP Code',
            message=f'Your OTP Code is: {otp_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response({
            "message": "Registration completed successfully, check the email for the OTP code"
        }, status=status.HTTP_201_CREATED)
    
class PongLoginView(APIView):
    def post(self, request):
        serializer = PongLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        otp_secret = user.otp_secret or pyotp.random_base32()
        user.otp_secret = otp_secret
        user.save()
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()

        send_mail(
            subject='OTP Code',
            message=f'Your OTP Code is: {otp_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            "message": "Authentication completed successfully, check the email for the OTP code"
        }, status=status.HTTP_200_OK)
    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        totp = pyotp.TOTP(user.otp_secret)
        if not totp.verify(otp_code):
            return Response(
                {"detail": "Invalid OTP code."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({"access": access_token, "refresh": refresh_token}, status=status.HTTP_200_OK)
