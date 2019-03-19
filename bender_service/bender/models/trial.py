from __future__ import unicode_literals
from django_extensions.db.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField
from django_extensions.db.fields import UUIDField
from django.conf import settings
from .experiment import Experiment
from .algo import Algo
from django.db import models


class Trial(TimeStampedModel, models.Model):
    id = UUIDField(primary_key=True)
    algo = models.ForeignKey(Algo, related_name="trials")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="trials")
    experiment = models.ForeignKey(Experiment, related_name="trials")
    parameters = JSONField()
    results = JSONField()
    comment = JSONField(null=True, blank=True)
    weight = models.FloatField(default=1)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Trial {} with algo {} of experiment {}'.format(self.pk, self.algo, self.experiment)
