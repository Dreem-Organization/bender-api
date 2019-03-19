from rest_framework import viewsets, pagination, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from ..models import Algo
from ..serializers import AlgoSerializer, AlgoSerializerUpdate, AlgoSerializerCreate, AlgoSerializerSuggest
from ..permissions import AlgoPermission
from ..throttling import AlgoThrottle
from ..filters import AlgoFilter
from benderopt.optimizer import optimizers as bender_optimizers
from benderopt.base import OptimizationProblem


class AlgoViewSet(viewsets.ModelViewSet):

    queryset = Algo.objects.all()
    serializer_class = AlgoSerializer
    permission_classes = (AlgoPermission,)
    throttle_classes = (AlgoThrottle,)
    filter_class = AlgoFilter
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action in ('create', ):
            serializer_class = AlgoSerializerCreate

        if self.action in ('update', 'partial_update'):
            serializer_class = AlgoSerializerUpdate

        return serializer_class

    @detail_route(methods=["post"])
    def suggest(self, request, pk=None):
        algo = self.get_object()
        serializer = AlgoSerializerSuggest(data=request.data, context={"algo": algo})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
