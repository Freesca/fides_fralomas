from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class PongUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_new_password = serializers.CharField(write_only=True, required=False)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'trophies', 'current_password', 'new_password', 'confirm_new_password', 'is_active']
        read_only_fields = ['trophies']

    def get_is_active(self, obj):
        inactivity_duration = timedelta(minutes=3)
        if obj.last_activity:
            time_since_last_activity = timezone.now() - obj.last_activity
            print(time_since_last_activity)
            return time_since_last_activity < inactivity_duration
        return False


    def validate(self, data):
        if 'new_password' in data or 'confirm_new_password' in data:
            if 'current_password' not in data:
                raise serializers.ValidationError("You must provide the current password to change it.")
            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError("The current password is incorrect.")
            if data['new_password'] != data['confirm_new_password']:
                raise serializers.ValidationError("The new passwords do not match.")
            
            validate_password(data['new_password'], self.instance)

        return data

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('confirm_new_password', None)

        instance = super().update(instance, validated_data)

        if new_password:
            instance.set_password(new_password)
            instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user == instance:
            representation['email'] = instance.email
            representation['extra_info'] = 'Reserved to the owner of the profile'
        else:
            representation.pop('email', None)
        return representation

class PongRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("The passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    
class PongLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)