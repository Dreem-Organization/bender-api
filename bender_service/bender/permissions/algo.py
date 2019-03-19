from rest_framework import permissions
from ..models import Experiment


class AlgoPermission(permissions.BasePermission):
    """Algo custom permission

    User need to be authenticated.
    If super user True

    Else adding protections for classic user.
        - Creation: Cannot create for another user.
                    Cannot create for another experience unless user in shared_with
    """

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated():

            if view.action == "create":
                experiment_pk = request.data.get("experiment")
                if not experiment_pk:  # Will be 400ed
                    return True

                if Experiment.objects.filter(pk=experiment_pk).exists():
                    experiment = Experiment.objects.get(pk=experiment_pk)
                    if (user == experiment.owner) or (user in experiment.shared_with.all()):
                        return True
                else:
                    return True  # will be 400ed

            elif view.action == "list":
                owner = request.GET.get("owner")
                if owner and owner == request.user.username:
                    return True

                experiment_pk = request.GET.get("experiment")
                if experiment_pk and Experiment.objects.filter(pk=experiment_pk).exists():
                    experiment = Experiment.objects.get(pk=experiment_pk)
                    if (request.user == experiment.owner or
                            request.user in experiment.shared_with.all()):
                            return True

            else:
                return True

        return False

    def has_object_permission(self, request, view, algo):
        user = request.user

        if user.is_authenticated():
            if algo.owner == request.user:
                return True
            elif view.action == "retrieve":
                if request.user in algo.experiment.shared_with.all():
                    return True

        return False
