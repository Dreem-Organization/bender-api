from rest_framework import serializers
from django.contrib.auth import get_user_model
from bender.serializers.experiment import ExperimentSerializerBasic
from django.db import transaction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    shared_experiments = ExperimentSerializerBasic(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'shared_experiments'
        )


class UserSerializerUsername(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
        )


class UserSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'shared_experiments'
        )

    def validate_email(self, value):
        """Check that email is available."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already used.")
        return value

    @transaction.atomic()
    def update(self, instance, validated_data):
        """Delete algos (and trials also) when removing from shared_experiment"""
        shared_experiments_before = list(instance.shared_experiments.all())
        instance = super(UserSerializerUpdate, self).update(instance, validated_data)
        not_shared_anymore = [experiment for experiment in shared_experiments_before
                              if experiment not in instance.shared_experiments.all()]
        for experiment in not_shared_anymore:
            instance.algos.filter(experiment=experiment).delete()
        return instance
