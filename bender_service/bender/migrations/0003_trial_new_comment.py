from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, transaction


def forwards_func(apps, schema_editor):
    Trial = apps.get_model("bender", "Trial")
    with transaction.atomic():
        for trial in Trial.objects.all():
            trial.new_comment = {"text": trial.comment}
            trial.save()


def reverse_func(apps, schema_editor):
    Trial = apps.get_model("bender", "Trial")
    with transaction.atomic():
        for trial in Trial.objects.all():
            trial.comment = trial.new_comment["text"]
            trial.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bender', '0002_auto_20170427_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='new_comment',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RemoveField(
            model_name='trial',
            name='comment',
        ),
        migrations.RenameField(
            model_name='trial',
            old_name='new_comment',
            new_name='comment',
        ),
    ]
