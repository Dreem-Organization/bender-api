from rest_framework import serializers
from bender.models import Experiment
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class MetricSerializer(serializers.Serializer):
    metric_name = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=("loss", "reward"))


class ExperimentSerializer(serializers.ModelSerializer):
    trial_count = serializers.SerializerMethodField()
    algo_count = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    owner = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    shared_with = serializers.SlugRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all(),
        slug_field='username'
    )

    def get_trial_count(self, instance):
        return instance.trials.count()

    def get_algo_count(self, instance):
        return instance.algos.count()

    def get_participants(self, instance):
        return (instance.trials.order_by('owner__username')
                .values_list('owner__username').distinct())

    class Meta:
        model = Experiment

        fields = (
            'id',
            'name',
            'description',
            'metrics',
            'dataset',
            'dataset_parameters',
            'trial_count',
            'algo_count',
            'owner',
            'participants',
            'shared_with',
            'created',
            'modified',
        )


class ExperimentSerializerBasic(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Experiment

        fields = (
            'id',
            'name',
            'owner',
        )


class ExperimentSerializerCreate(serializers.ModelSerializer):

    metrics = MetricSerializer(many=True, allow_empty=False)

    class Meta:
        model = Experiment

        fields = (
            'id',
            'name',
            'description',
            'dataset',
            'dataset_parameters',
            'metrics',
        )

    def validate_name(self, value):
        """ Chech that name does not exist for same experiment.

        Need to be added because owner is added just befor creation, not present at validation time.
        """
        if value in self.context["request"].user.experiments.values_list('name', flat=True):
            raise serializers.ValidationError("Experiment with same name already exist!")
        return value

    def validate_metrics(self, value):
        """Check that there are not metric name duplicates"""
        metric_names = [x["metric_name"] for x in value]
        if len(set(metric_names)) != len(metric_names):
            raise serializers.ValidationError("Need at least one metric!")
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        experiment = Experiment.objects.create(**validated_data)
        return experiment


class ExperimentSerializerUpdate(serializers.ModelSerializer):
    shared_with = serializers.SlugRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Experiment

        fields = (
            'id',
            'description',
            'dataset',
            'dataset_parameters',
            'shared_with',
        )

    def validate(self, data):
        """ Check that owner is not in shared_with """
        if self.context["view"].get_object().owner in data.get('shared_with', []):
            raise serializers.ValidationError("Owner should not be in shared_with argument!")
        return data

    @transaction.atomic()
    def update(self, instance, validated_data):
        """Delete algos (and trials also) when removing a user from shared_with"""
        shared_with_before = list(instance.shared_with.all())  # list force evaluation of query
        instance = super(ExperimentSerializerUpdate, self).update(instance, validated_data)
        not_shared_anymore = [user for user in shared_with_before
                              if user not in instance.shared_with.all()]
        for user in not_shared_anymore:
            user.algos.filter(experiment=instance).delete()
        return instance
