# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_auto_20151013_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='forum',
            name='short_name',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
