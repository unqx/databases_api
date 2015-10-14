# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20151013_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='owner_id',
            field=models.IntegerField(default=1),
        ),
    ]
