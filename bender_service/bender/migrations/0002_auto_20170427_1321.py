# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-27 13:21
from __future__ import unicode_literals

import bender.models.user
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bender', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', bender.models.user.CustomUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='parameter',
            name='category',
            field=models.CharField(blank=True, choices=[('categorical', 'Categorical parameter'), ('uniform', 'Uniformly distributed parameter'), ('normal', 'Normally distributed parameter'), ('lognormal', 'Log-Normally distributed parameter'), ('loguniform', 'Log-Uniformly distributed parameter')], max_length=50, null=True),
        ),
    ]