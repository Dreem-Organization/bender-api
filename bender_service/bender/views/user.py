from rest_framework import mixins, viewsets, pagination, filters, status, response
from rest_framework.decorators import list_route
from ..models import User
from ..serializers import (UserSerializer,
                           UserSerializerUpdate,
                           UserSerializerUsername)
from ..permissions import UserPermission
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings


class UserViewSet(mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action in ('update', 'partial_update'):
            serializer_class = UserSerializerUpdate

        if self.action in ('list', ):
            if self.request.user.is_superuser:
                serializer_class = UserSerializer
            else:
                serializer_class = UserSerializerUsername

        return serializer_class

    @list_route(methods=["post"])
    def contact(self, request):
        html_message = loader.render_to_string('bender/contact_success.html')
        send_mail(
            '[BENDER WEB CLIENT] {}'.format(request.data['title']),
            request.data['content'] + "\n\n\n\nuser: " + str(request.user.username),
            request.data['email'],
            settings.EMAIL_HOST_TO,
            fail_silently=True,
        )
        send_mail(
            '[BENDER WEB CLIENT] Contact request well recieved !',
            '',
            'no-reply',
            [request.data['email']],
            fail_silently=True,
            html_message=html_message
        )
        return response.Response({}, status=status.HTTP_200_OK)
