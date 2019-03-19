import django_filters
from ..models import Experiment


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    owner = django_filters.CharFilter(name="owner__username")
    shared_with = django_filters.CharFilter(name="shared_with__username")
    o = django_filters.OrderingFilter(
        fields=(
            ('created', 'date'),
        ),
    )

    class Meta:
        model = Experiment
        fields = ['dataset', 'name']
