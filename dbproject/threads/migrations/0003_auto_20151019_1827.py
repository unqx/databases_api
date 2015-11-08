# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0002_thread_subscribed'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='thread',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='thread',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='thread',
            name='posts',
            field=models.IntegerField(default=0),
        ),
    ]
