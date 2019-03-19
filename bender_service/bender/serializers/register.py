from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers


class CustomRegisterSerializer(RegisterSerializer):
    tos_accepted = serializers.ChoiceField(choices=[True, ], allow_blank=False)
