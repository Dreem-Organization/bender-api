from rest_framework import viewsets, pagination
from django.contrib.auth import get_user_model
from ..models import Experiment
from ..serializers import (ExperimentSerializer,
                           ExperimentSerializerUpdate,
                           ExperimentSerializerCreate)
from ..permissions import ExperimentPermission
from ..throttling import ExperimentThrottle
from ..filters import ExperimentFilter

User = get_user_model()


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = (ExperimentPermission,)
    throttle_classes = (ExperimentThrottle,)
    filter_class = ExperimentFilter
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action in ('create', ):
            serializer_class = ExperimentSerializerCreate

        if self.action in ('update', 'partial_update'):
            serializer_class = ExperimentSerializerUpdate

        return serializer_class
