from rest_framework import serializers
from bender.models import Trial
from django.contrib.auth import get_user_model
import numpy as np

User = get_user_model()


class TrialSerializer(serializers.ModelSerializer):
    algo_name = serializers.SerializerMethodField()
    owner = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    def get_algo_name(self, instance):
        return instance.algo.name

    class Meta:
        model = Trial
        fields = (
            'id',
            'algo',
            'experiment',
            'owner',
            'parameters',
            'results',
            'comment',
            'algo_name',
            'created',
            'modified',
            'weight',
        )


class TrialSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Trial
        fields = (
            'id',
            'algo',
            'parameters',
            'results',
            'comment',
            'weight',
        )

    def create(self, validated_data):
        """Add request.user as owner and algo.experiment as experiment automatically."""
        validated_data['owner'] = self.context['request'].user
        validated_data['experiment'] = validated_data['algo'].experiment
        return super(TrialSerializerCreate, self).create(validated_data)

    def validate(self, data):
        """Check that results/parameters keys are same as experiment.metrics/algo.parameters"""
        if set(data["parameters"]) != set(data["algo"].parameters.values_list("name", flat=True)):
            raise serializers.ValidationError("Parameters are different from algo parameters.")
        if set(data["results"].keys()) != set([x["metric_name"] for x in data["algo"].experiment.metrics]):
            raise serializers.ValidationError(
                "Results keys are differents from experiment metrics.")

        if None in data["parameters"].values():
            raise serializers.ValidationError("None is an invalid value for a parameter")

        for parameter_value in data["parameters"].values():
            if (type(parameter_value) == float) and np.isnan(parameter_value):
                raise serializers.ValidationError("Nan is an invalid value for a parameter")

        if None in data["results"].values():
            raise serializers.ValidationError("None is an invalid value for a parameter")

        for result in data["results"].values():
            if (type(result) == float) and np.isnan(result):
                raise serializers.ValidationError("Nan is an invalid value for a parameter")

        return data
