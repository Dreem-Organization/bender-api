from django.db.models.expressions import RawSQL
import django_filters
from ..models import Trial


class TrialFilter(django_filters.rest_framework.FilterSet):
    owner = django_filters.CharFilter(name="owner__username")
    o_results = django_filters.CharFilter(method='filter_json')
    o_parameters = django_filters.CharFilter(method='filter_json')
    o = django_filters.OrderingFilter(
        fields=(
            ('created', 'date'),
        ),
    )

    class Meta:
        model = Trial
        fields = ['experiment', 'algo']

    def filter_json(self, queryset, name, value):

        key = name.split("o_")[1]
        reverse = False
        if value[0] == "-":
            reverse = True
            value = value[1:]

        queryset = queryset.order_by(RawSQL("{}->>%s".format(key), (value,)))

        if reverse:
            queryset = queryset.reverse()

        return queryset
