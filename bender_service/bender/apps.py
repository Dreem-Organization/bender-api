from __future__ import unicode_literals

from django.apps import AppConfig


class BenderConfig(AppConfig):
    name = 'bender'
    verbose_name = "bender"

    def ready(self):
        """http://stackoverflow.com/questions/2719038/where-should-signal
        -handlers-live-in-a-django-project"""
        import bender.signals.handlers
