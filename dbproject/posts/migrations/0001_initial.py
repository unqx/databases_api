# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forum_id', models.IntegerField()),
                ('thread_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('message', models.TextField(max_length=1000)),
                ('date', models.DateTimeField()),
                ('parent', models.IntegerField(default=None, null=True)),
                ('path', models.CharField(default=None, max_length=1000, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_highlited', models.BooleanField(default=False)),
                ('is_spam', models.BooleanField(default=False)),
                ('is_edited', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'post',
            },
        ),
    ]
