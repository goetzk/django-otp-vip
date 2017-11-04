# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.db import models

# Create your models here.

from django_otp.models import Device as OTP_Device
from utils import send_user_auth_push, poll_user_auth_push, validate_token_data


class PushDevice(OTP_Device):
  """Records devices capable of receiving Symantec VIP push authentication
  requests"""
  last_updated = models.DateTimeField(auto_now=True, verbose_name='Updated at')
  latest_transaction_id = models.CharField(max_length=30, editable=False)

  def generate_challenge(self):
    """Send request for a push to Symantec VIP servers
    This method runs self.save() to record the transaction id.
    """
    logger.debug('Calling send_user_auth_push and recording its transaction ID')
    auth_attempt = send_user_auth_push(self.user)
    logger.debug('Auth attempt dictionary: %s' % auth_attempt.__dict__)
    self.latest_transaction_id = auth_attempt.transaction_id
    self.save(update_fields=['latest_transaction_id'])
    return str('Sent (Check your device).')

  def verify_token(self):
    """Poll Symantec VIP service for a response to the push request"""
    # Do we have a transaction ID to query?
    if not self.latest_transaction_id:
      return False
    # poll_user_auth_push will run for the time configured in
    # VIP_POLL_SLEEP_SECONDS times VIP_POLL_SLEEP_MAX_COUNT
    logger.debug('Running poll_user_auth_push with transaction ID %s' % self.latest_transaction_id)
    # This returns True or False depending on the result
    return poll_user_auth_push(self.latest_transaction_id)


class TokenDevice(OTP_Device):
  """Records VIP compatible devices which generate authentication codes"""
  token_code = models.CharField(max_length=30, default='')

  def verify_token(self, token):
    """Check with Symantec VIP service if this token should be considered
    valid"""
    self.token_code = token
    self.save()
    logger.debug("Calling validate_token_data with user {0} and token {1}".format(self.user, token))
    return validate_token_data(self.user, token)

# FIXME: Do these two have existing classes i can override?
# TODO: This will have to wait until I have a chance to set up SMS on VIP
# class SmsDevice(OTP_Device):
#   """Records devices which can receive SMS' via VIP"""
#   # FIXME: needs to check if user has specified phone number. Bail if they haven't.
# if phone nubmer in user profile, use it, else number passed as param to init, use it. else fail
#   pass

# class CallDevice(OTP_Device)
#   """Records devices which can receive a call via VIP"""
#   # FIXME: needs to check if user has specified phone number. Bail if they haven't.
# if phone nubmer in user profile, use it, else number passed as param to init, use it. else fail
#   pass

