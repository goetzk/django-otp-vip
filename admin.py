# -*- coding: utf-8 -*-
"""Set up Django Admin to access VIP records.

These are purely for viewing purposes
"""
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .credential_models import VipPushCredential, VipTokenCredential
from models import VipUser

# http://django-otp-official.readthedocs.io/en/latest/auth.html?highlight=form#the-admin-site

@admin.register(VipUser)
class UserAdmin(admin.ModelAdmin):
  """Provides administrative functions for the VIP User ."""

  readonly_fields = ['vip_user_id', 'vip_created_at', 'status', 'bindings_count', 'pin_set', 'pin_expiration_time', 'temp_password_set']
  list_filter = ['vip_created_at', 'status', 'temp_password_set', 'pin_expiration_time']
  list_display = ['user', 'vip_user_id', 'status', 'vip_created_at', 'bindings_count']
  search_fields = ['vip_user_id', 'user__username', '']

@admin.register(VipPushCredential)
class PushCredentialAdmin(admin.ModelAdmin):
  """Provides administrative functions for VIP Push credentials."""

  # FIXME: all fields read only
  readonly_fields = ['credential_id']
  list_filter = ['credential_type', 'credential_status', 'token_form_factor', 'token_kind', 'last_authn_time']
  search_fields = ['credential_id', 'user__username', 'token_kind', 'token_adaptor', 'push_enabled', 'friendly_name']
  list_display = ['user', 'credential_id', 'credential_type', 'friendly_name', 'last_authn_time']

@admin.register(VipTokenCredential)
class TokenCredentialAdmin(admin.ModelAdmin):
  """Provides administrative functions for VIP Token credentials."""

  list_filter = [ 'confirmed']
  search_fields = ['latest_transaction_id', 'user__username', 'confirmed']

