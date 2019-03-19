from rest_framework import throttling, exceptions
from django.conf import settings
from ..models import Experiment


class ExperimentThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):
        if view.action == "create":
            if (Experiment.objects.filter(owner=request.user).count() >=
                    settings.BENDER_MAX_EXPERIMENT_PER_USER):
                raise exceptions.Throttled(detail="Max number of experiment reached.")

        if view.action in ("partial_update", "update"):
            shared_with = request.data.get("shared_with")
            if shared_with and type(shared_with) == list:
                if len(shared_with) > settings.BENDER_MAX_SHARED_WITH_PER_EXPERIMENT:
                    raise exceptions.Throttled(detail="Max shared with reached!")

        return True
