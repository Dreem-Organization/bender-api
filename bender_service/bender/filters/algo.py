import django_filters
from ..models import Algo


class AlgoFilter(django_filters.rest_framework.FilterSet):
    owner = django_filters.CharFilter(name="owner__username")
    o = django_filters.OrderingFilter(
        fields=(
            ('created', 'date'),
        ),
    )

    class Meta:
        model = Algo
        fields = ['experiment', 'name']
