# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-03 17:27
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bender', '0005_remove_experiment_metrics'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='metrics',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[{'metric_name': 'accuracy', 'type': 'reward'}]),
            preserve_default=False,
        ),
    ]
