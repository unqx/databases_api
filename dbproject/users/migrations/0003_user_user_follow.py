# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20151014_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_follow',
            field=models.ManyToManyField(related_name='_user_follow_+', to='users.User'),
        ),
    ]
