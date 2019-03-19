from __future__ import unicode_literals
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings
from .experiment import Experiment


class Algo(TimeStampedModel, models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    experiment = models.ForeignKey(Experiment, related_name="algos")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="algos")
    description = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('experiment', 'name',)
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def is_search_space_defined(self):
        from bender.models import Parameter
        search_space_defined = True
        for parameter in self.parameters.exclude(category=Parameter.DESCRIPTIVE):
            if not parameter.category or not parameter.search_space:
                search_space_defined = False
                break
        return search_space_defined

    def get_optimization_problem(self, metric):
        from bender.models import Parameter
        data = None
        if self.is_search_space_defined():
            data = {
                "parameters": [
                    {
                        "name": parameter.name,
                        "category": parameter.category,
                        "search_space": parameter.search_space
                    }
                    for parameter in self.parameters.all() if parameter.category != Parameter.DESCRIPTIVE
                ],
                "observations": [
                    {
                        "sample": trial.parameters,
                        "loss": (trial.results[metric["metric_name"]]
                                 if metric["type"] == "loss" else -trial.results[metric["metric_name"]]),
                        "weight": trial.weight
                    }
                    for trial in self.trials.all()
                ]
            }
        return data
