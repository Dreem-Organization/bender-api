from django.contrib.auth.models import AbstractUser, UserManager
from allauth.account.models import EmailAddress
from django.db import models


class CustomUserManager(UserManager):

    def create_user(self, *args, **kwargs):
        if ("username" not in kwargs.keys() or
            "email" not in kwargs.keys() or
                "password" not in kwargs.keys()):
            raise ValueError("Need username, email and password")
        user = super(CustomUserManager, self).create_user(*args, **kwargs)
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=True)
        return user

    def create_superuser(self, *args, **kwargs):
        if ("username" not in kwargs.keys() or
            "email" not in kwargs.keys() or
                "password" not in kwargs.keys()):
            raise ValueError("Need username, email and password")
        superuser = super(CustomUserManager, self).create_superuser(*args, **kwargs)
        EmailAddress.objects.create(user=superuser,
                                    email=superuser.email,
                                    primary=True,
                                    verified=True)
        return superuser


class User(AbstractUser):
    tos_accepted = models.BooleanField(default=True)

    objects = CustomUserManager()
