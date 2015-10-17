# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('about', models.TextField(blank=True)),
                ('is_anonymous', models.BooleanField(default=0)),
            ],
        ),
    ]
