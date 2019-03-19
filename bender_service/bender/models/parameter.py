from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from .algo import Algo
from django.db import models


class Parameter(models.Model):

    DESCRIPTIVE = "descriptive"
    CATEGORICAL = "categorical"
    UNIFORM = "uniform"
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    LOGUNIFORM = "loguniform"

    PARAMETER_TYPE = (
        (DESCRIPTIVE, "Descriptive parameter"),
        (CATEGORICAL, "Categorical parameter"),
        (UNIFORM, "Uniformly distributed parameter"),
        (NORMAL, "Normally distributed parameter"),
        (LOGNORMAL, "Log-Normally distributed parameter"),
        (LOGUNIFORM, "Log-Uniformly distributed parameter"),
    )

    algo = models.ForeignKey(Algo, related_name="parameters")
    name = models.CharField(max_length=150)
    category = models.CharField(choices=PARAMETER_TYPE, max_length=50, blank=True, null=True)
    search_space = JSONField(blank=True, null=True)

    class Meta:
        unique_together = (("algo", "name"),)

    def __str__(self):
        return self.name
