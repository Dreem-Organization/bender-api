from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from django.db import transaction
from bender.models import Algo, Trial, Parameter
from benderopt.base import OptimizationProblem
from benderopt.optimizer import optimizers as bender_optimizers
from bender.serializers.parameter import (
    ParameterSerializer,
    ParameterSerializerCreate,
    ParameterSerializerUpdate,
)

User = get_user_model()


class NoSearchSpaceError(APIException):
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = "Define paramter search space to get suggestion."
    default_code = "no_content"


class AlgoSerializerSuggest(serializers.Serializer):
    optimizer = serializers.ChoiceField(
        choices=("random", "parzen_estimator"), default="parzen_estimator"
    )
    metric = serializers.CharField(max_length=50)
    minimum_observations = serializers.IntegerField(
        min_value=1, max_value=1000, default=30
    )

    def parse_optimization_problem(self, data):
        metric = self.parse_metric(data)
        optimization_problem_data = self.context["algo"].get_optimization_problem(
            metric
        )
        if optimization_problem_data is None:
            # FIXME: Could be standard ValidationError with a code
            # argument, available only in next versions of DRF
            raise NoSearchSpaceError()
        optimization_problem = OptimizationProblem.from_list(
            optimization_problem_data["parameters"]
        )
        optimization_problem.add_observations_from_list(
            optimization_problem_data["observations"]
        )
        return optimization_problem

    def parse_metric(self, data):
        if "metric" not in data or not data["metric"]:
            raise serializers.ValidationError({"metric": "Missing metric argument"})
        tmp = [
            metric
            for metric in self.context["algo"].experiment.metrics
            if metric["metric_name"] == data["metric"]
        ]
        if len(tmp) != 1:
            raise serializers.ValidationError({"metric": "Unknown metric asked"})
        return tmp[0]

    def to_internal_value(self, data):
        res = super().to_internal_value(data)
        res["optimization_problem"] = self.parse_optimization_problem(data)
        return res

    def to_representation(self, validated_data):
        kwargs = {"optimization_problem": validated_data["optimization_problem"]}
        if validated_data["optimizer"] != "random":
            kwargs["minimum_observations"] = validated_data["minimum_observations"]
        sample = bender_optimizers.get(validated_data["optimizer"])(**kwargs).suggest()
        return sample


class AlgoSerializer(serializers.ModelSerializer):
    trial_count = serializers.SerializerMethodField("trial_counter")
    is_search_space_defined = serializers.SerializerMethodField()
    owner = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    parameters = ParameterSerializer(many=True)

    def trial_counter(self, instance):
        return Trial.objects.filter(algo=instance.id).count()

    def get_is_search_space_defined(self, instance):
        return instance.is_search_space_defined()

    class Meta:
        model = Algo
        fields = (
            "id",
            "name",
            "experiment",
            "owner",
            "parameters",
            "description",
            "trial_count",
            "created",
            "modified",
            "is_search_space_defined",
        )


class AlgoSerializerCreate(serializers.ModelSerializer):
    parameters = ParameterSerializerCreate(many=True)
    is_search_space_defined = serializers.SerializerMethodField()

    class Meta:
        model = Algo
        fields = (
            "id",
            "name",
            "experiment",
            "description",
            "parameters",
            "is_search_space_defined",
        )
        read_only_fields = ("id", "is_search_space_defined")

    def validate(self, data):
        """ Check that owner is not in shared_with """
        if len(data["parameters"]) != len(set([x["name"] for x in data["parameters"]])):
            raise serializers.ValidationError(
                "Two or more parameters have the same name!"
            )

        return data

    @transaction.atomic()
    def create(self, validated_data):
        parameters_data = validated_data.pop("parameters")
        validated_data["owner"] = self.context["request"].user
        algo = super(AlgoSerializerCreate, self).create(validated_data)
        for parameter in parameters_data:
            Parameter.objects.create(algo=algo, **parameter)
        return algo

    def get_is_search_space_defined(self, instance):
        return instance.is_search_space_defined()


class AlgoSerializerUpdate(serializers.ModelSerializer):
    parameters = ParameterSerializerUpdate(many=True)

    class Meta:
        model = Algo
        fields = ("id", "name", "description", "parameters")

    def validate(self, data):
        """ Check that owner is not in shared_with """
        algo = self.instance
        data_parameters = data.get("parameters", [])
        if len(data_parameters) > 0 and algo.trials.count() > 0:
            data_parameters_name = set([x["name"] for x in data_parameters])
            algo_parameters_name = set([x.name for x in algo.parameters.all()])
            if len(data_parameters_name.difference(algo_parameters_name)) > 0:
                raise serializers.ValidationError(
                    "Cannot add a new paramter to an algo with tria" "ls"
                )
            for data_parameter in data_parameters:
                parameter = algo.parameters.get(name=data_parameter["name"])
                if parameter.category != data_parameter["category"]:
                    raise serializers.ValidationError(
                        "Cannot change the category of an existing "
                        "parameter after trials have been made"
                    )

        return data

    @transaction.atomic()
    def update(self, algo, validated_data):
        parameters_data = validated_data.pop("parameters", None)
        algo = super(AlgoSerializerUpdate, self).update(algo, validated_data)
        if parameters_data:
            for parameter_data in parameters_data:
                if parameter_data.get("name") is not None:
                    parameter, _ = Parameter.objects.get_or_create(
                        algo=algo, name=parameter_data["name"]
                    )
                    parameter.category = parameter_data.get("category")
                    parameter.search_space = parameter_data.get("search_space")
                    parameter.save()
        return algo
