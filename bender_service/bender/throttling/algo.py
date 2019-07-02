from rest_framework import throttling, exceptions
from django.conf import settings
from ..models import Experiment


class AlgoThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):

        if request.user.pk in settings.WHITELIST:
            return True

        if view.action == "create":
            experiment_pk = request.data.get('experiment')
            if experiment_pk:
                if Experiment.objects.filter(pk=experiment_pk).exists():
                    experiment = Experiment.objects.get(pk=experiment_pk)
                    if (experiment.algos.count() >= settings.BENDER_MAX_ALGO_PER_EXPERIMENT):
                        raise exceptions.Throttled(
                            detail="Max number of algo reached for this experiment.")
        return True
