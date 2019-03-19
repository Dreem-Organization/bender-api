# encoding: utf-8
from django.dispatch import receiver
from django.db import models
from django.contrib.auth import get_user_model
from .helpers import generate_demo

User = get_user_model()


@receiver(models.signals.post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    """Remove S3 H5File instance."""
    if kwargs["created"]:
        generate_demo(instance)
