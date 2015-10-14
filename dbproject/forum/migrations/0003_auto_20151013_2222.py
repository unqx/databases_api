# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20151013_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='is_deleted',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='forum',
            name='owner_id',
            field=models.EmailField(default=1, max_length=100),
        ),
        migrations.AddField(
            model_name='forum',
            name='short_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='forum',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
