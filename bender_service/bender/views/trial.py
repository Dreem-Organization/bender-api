from rest_framework import viewsets, pagination, mixins
from ..models import Trial
from ..serializers import TrialSerializer, TrialSerializerCreate
from ..permissions import TrialPermission
from ..throttling import TrialThrottle
from ..filters import TrialFilter


class TrialViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer
    permission_classes = (TrialPermission,)
    throttle_classes = (TrialThrottle,)
    filter_class = TrialFilter
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action in ('create', ):
            serializer_class = TrialSerializerCreate

        return serializer_class
