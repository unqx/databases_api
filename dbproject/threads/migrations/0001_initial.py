# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forum_id', models.IntegerField()),
                ('title', models.CharField(max_length=60)),
                ('is_closed', models.BooleanField(default=False)),
                ('user_id', models.IntegerField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('message', models.TextField(max_length=1000)),
                ('slug', models.CharField(max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'thread',
            },
        ),
    ]
