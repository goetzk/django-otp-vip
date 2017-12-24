# -*- coding: utf-8 -*-
"""Generic and base models."""
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.db import models

from django.contrib.auth.models import User as User

from django_otp.models import Device as OTP_Device


# VIP credential models are in credential_models.py

class VipUser(models.Model):
  """VIP user specification.

  All information we've retrieved about this user from the API is recorded in
  this model.
  """

  user = models.OneToOneField(User, verbose_name='Members username')
  # This should always be identical to user.email
  vip_user_id = models.CharField(max_length=255, default=False)
  vip_created_at = models.DateTimeField(verbose_name='Creation time per VIP API', blank=True)
  status = models.CharField(max_length=10, default=False) # Could be Active, Locked, disabled
  bindings_count = models.PositiveSmallIntegerField(default=0)
  pin_set = models.NullBooleanField(default=False, null=True)
  pin_expiration_time = models.NullBooleanField(default=False, null=True)
  temp_password_set = models.DateTimeField(null=True, blank=True)

  def __unicode__(self):
    """Return model description based on user name and user id."""
    return '%s (%s)' % (self.user.username, self.vip_user_id)

class VipBaseCredential(OTP_Device):
  """Abstract base class for other VIP credentials.

  Values common to all VIP Credentials, this is the majority of the specification
  for all current types of devices.

  https://docs.djangoproject.com/en/1.11/topics/db/models/#abstract-base-classes
  """

  # As of writing, the following come from OTP_Device:
  # user (FK, user object)
  # name (string, human friendly name for 'token' (credential)), used to store friendlyName data
  # confirmed (bool, has this been confirmed valid.)

# FIXME: These all come from a software token and many may not actually be universal
  credential_id = models.CharField(max_length=20, default=False, unique=True)
  credential_type = models.CharField(max_length=20, default=False)
  credential_status = models.CharField(max_length=20, null=True)
  friendly_name = models.CharField(max_length=20, default=False)
  token_form_factor = models.CharField(max_length=20, default=False)
  token_kind = models.CharField(max_length=20, default=False)
  token_adaptor = models.CharField(max_length=20, default=False)
  token_status = models.CharField(max_length=20, default=False)
  token_expiration_date = models.DateTimeField()
  token_last_update = models.DateTimeField()
  bind_status = models.CharField(max_length=20, default=False)
  bind_time = models.DateTimeField()
  friendly_name = models.CharField(max_length=20, default=False)
  last_authn_time = models.DateTimeField(null=True, blank=True)
  # Same as transaction_id?
  last_authn_id = models.CharField(max_length=20, default=False, null=True)
  push_enabled = models.BooleanField(default=False)

  class Meta:
    """Class meta configuration.

    Currently only abstract = True is defined here
    """

    abstract = True

  def save(self, *args, **kwargs):
    """Override save to modify 'confirmed' status."""
    if self.token_status and self.bind_status and self.credential_status:
      self.confirmed = True
    else:
      self.confirmed = False
    super(VipBaseCredential, self).save(*args, **kwargs)

