# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import PushDevice, TokenDevice


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
  """Provides administrative functions for the model."""
  readonly_fields = ['last_updated', 'latest_transaction_id']
  list_filter = ['last_updated', 'confirmed']
  search_fields = ['latest_transaction_id', 'user__username', 'confirmed']

@admin.register(TokenDevice)
class TokenDeviceAdmin(admin.ModelAdmin):
  """Provides administrative functions for the model."""
  list_filter = [ 'confirmed']
  search_fields = ['latest_transaction_id', 'user__username', 'confirmed']

