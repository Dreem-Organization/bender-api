from rest_framework import serializers
from bender.models import Parameter
from benderopt.validation import validate_search_space


class ParameterSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Parameter
        fields = (
            'algo',
            'name',
            'category',
            'search_space',
            'category_display',
        )

    def get_category_display(self, obj):
        return obj.get_category_display()


class ParameterSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = (
            'name',
            'category',
            'search_space',
        )

    def validate(self, data):
        if data.get("category") and data.get("search_space"):
            try:
                validate_search_space[data["category"]](data["search_space"])
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return data


class ParameterSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = (
            'name',
            'category',
            'search_space',
        )

    def validate(self, data):
        if data.get("category") and data.get("search_space"):
            try:
                validate_search_space[data["category"]](data["search_space"])
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return data
