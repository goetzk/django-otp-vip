# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VipPushCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('credential_id', models.CharField(default=False, unique=True, max_length=20)),
                ('credential_type', models.CharField(default=False, max_length=20)),
                ('credential_status', models.CharField(max_length=20, null=True)),
                ('token_form_factor', models.CharField(default=False, max_length=20)),
                ('token_kind', models.CharField(default=False, max_length=20)),
                ('token_adaptor', models.CharField(default=False, max_length=20)),
                ('token_status', models.CharField(default=False, max_length=20)),
                ('token_expiration_date', models.DateTimeField()),
                ('token_last_update', models.DateTimeField()),
                ('bind_status', models.CharField(default=False, max_length=20)),
                ('bind_time', models.DateTimeField()),
                ('last_authn_time', models.DateTimeField(null=True, blank=True)),
                ('last_authn_id', models.CharField(default=False, max_length=20, null=True)),
                ('push_enabled', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name=b'Updated at')),
                ('latest_transaction_id', models.CharField(max_length=30, editable=False)),
                ('attribute_platform', models.CharField(max_length=30, editable=False)),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VipTokenCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('credential_id', models.CharField(default=False, unique=True, max_length=20)),
                ('credential_type', models.CharField(default=False, max_length=20)),
                ('credential_status', models.CharField(max_length=20, null=True)),
                ('token_form_factor', models.CharField(default=False, max_length=20)),
                ('token_kind', models.CharField(default=False, max_length=20)),
                ('token_adaptor', models.CharField(default=False, max_length=20)),
                ('token_status', models.CharField(default=False, max_length=20)),
                ('token_expiration_date', models.DateTimeField()),
                ('token_last_update', models.DateTimeField()),
                ('bind_status', models.CharField(default=False, max_length=20)),
                ('bind_time', models.DateTimeField()),
                ('last_authn_time', models.DateTimeField(null=True, blank=True)),
                ('last_authn_id', models.CharField(default=False, max_length=20, null=True)),
                ('push_enabled', models.BooleanField(default=False)),
                ('token_code', models.CharField(default=b'', max_length=30)),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VipUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vip_user_id', models.CharField(default=False, max_length=255)),
                ('vip_created_at', models.DateTimeField(verbose_name='Creation time per VIP API', blank=True)),
                ('status', models.CharField(default=False, max_length=10)),
                ('bindings_count', models.PositiveSmallIntegerField(default=0)),
                ('pin_set', models.NullBooleanField(default=False)),
                ('pin_expiration_time', models.NullBooleanField(default=False)),
                ('temp_password_set', models.DateTimeField(null=True, blank=True)),
                ('user', models.OneToOneField(verbose_name='Members username', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
