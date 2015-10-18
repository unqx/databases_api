# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_user_follow'),
        ('threads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='subscribed',
            field=models.ManyToManyField(to='users.User', db_table=b'subscriptions'),
        ),
    ]
