# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .device_models import VipPushDevice, VipTokenDevice
from models import VipUser


@admin.register(VipUser)
class UserAdmin(admin.ModelAdmin):
  """Provides administrative functions for the model."""
  readonly_fields = ['vip_user_id', 'vip_created_at', 'status', 'bindings_count', 'pin_set', 'pin_expiration_time', 'temp_password_set']
  list_filter = ['vip_created_at', 'status', 'temp_password_set', 'pin_expiration_time']
  list_display = ['user', 'vip_user_id', 'status', 'vip_created_at', 'bindings_count']
  search_fields = ['vip_user_id', 'user__username', '']

@admin.register(VipPushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
  """Provides administrative functions for the model."""
  # FIXME: all fields read only
  readonly_fields = ['credential_id']
  list_filter = ['credential_type', 'credential_status', 'token_form_factor', 'token_kind', 'last_authn_time']
  search_fields = ['credential_id', 'user__username', 'token_kind', 'token_adaptor', 'push_enabled', 'friendly_name']
  list_display = ['user', 'credential_id', 'credential_type', 'friendly_name', 'last_authn_time']

@admin.register(VipTokenDevice)
class TokenDeviceAdmin(admin.ModelAdmin):
  """Provides administrative functions for the model."""
  list_filter = [ 'confirmed']
  search_fields = ['latest_transaction_id', 'user__username', 'confirmed']

