from rest_framework import permissions
from ..models import Algo, Experiment


class TrialPermission(permissions.BasePermission):
    """ """

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated():

            if view.action == "create":
                algo_pk = request.data.get("algo")

                if not algo_pk:  # Will be 400ed
                    return True

                if Algo.objects.filter(pk=algo_pk).exists():
                    algo = Algo.objects.get(pk=algo_pk)
                    if (user == algo.owner):
                        return True
                else:
                    return True  # will be 400ed

            elif view.action == "list":

                owner = request.GET.get("owner")
                if owner and owner == request.user.username:
                    return True

                algo_pk = request.GET.get("algo")
                if algo_pk and Algo.objects.filter(pk=algo_pk).exists():
                    algo = Algo.objects.get(pk=algo_pk)
                    if (request.user == algo.owner or
                            request.user in algo.experiment.shared_with.all()):
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

    def has_object_permission(self, request, view, trial):
        user = request.user

        if user.is_authenticated():
            if trial.owner == request.user:
                return True

        return False
