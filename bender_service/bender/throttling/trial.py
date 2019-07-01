from rest_framework import throttling, exceptions
from django.conf import settings
from ..models import Algo


class TrialThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):

        if str(request.user) in settings.WHITELIST:
            return True

        if view.action == "create":
            algo_pk = request.data.get('algo')
            if algo_pk:
                if Algo.objects.filter(pk=algo_pk).exists():
                    algo = Algo.objects.get(pk=algo_pk)
                    if (algo.trials.count() >= settings.BENDER_MAX_TRIALS_PER_ALGO):
                        raise exceptions.Throttled(
                            detail="Max number of trials reached for this algo.")
        return True
