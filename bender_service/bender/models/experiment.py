from __future__ import unicode_literals
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.db import models


class Experiment(TimeStampedModel, models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="experiments")
    metrics = JSONField()
    dataset = models.CharField(max_length=100, null=True, blank=True)
    dataset_parameters = JSONField(null=True, blank=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         related_name="shared_experiments",
                                         blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('owner', 'name'),)
        ordering = ('-modified', )
