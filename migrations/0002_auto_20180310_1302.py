# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_vip', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vippushcredential',
            name='friendly_name',
            field=models.CharField(default=False, max_length=250),
        ),
        migrations.AddField(
            model_name='viptokencredential',
            name='friendly_name',
            field=models.CharField(default=False, max_length=250),
        ),
    ]
