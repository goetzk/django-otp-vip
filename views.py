# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from django_otp_vip.utils import send_user_auth_push, poll_user_auth_push, validate_token_data

from django_otp_vip.forms import PushForm, TokenForm

import logging
logger = logging.getLogger(__name__)


@login_required
def run_otp(request):
  """This function is to perform 'other' user validation, for example 2nd factor
  checks. Override this view per the documentation if using this functionality.
  """

  display_template='django_otp_vip/validate_vip.html'

  logger.debug('In run_otp view')

  def perform_second_factor_pin(user, token_code):
    return validate_token_data(user, token_code)

  def perform_second_factor_push(user):
    """Send request for a second factor push to Symantec and poll for a result"""
    logger.debug('In run_otp\'s perform_second_factor_push function')

    # FIXME: catch errors and return PermissionDenied + helpful error
    logger.debug('Calling send_user_auth_push and recording its transaction ID')
    auth_attempt = send_user_auth_push(user)
    # VIP_POLL_SLEEP_SECONDS times VIP_POLL_SLEEP_MAX_COUNT
    logger.debug('Running poll_user_auth_push with transaction ID %s' % auth_attempt.transaction_id)
    # This returns True or False depending on the result
    return poll_user_auth_push(auth_attempt.transaction_id)

  # if this is a POST request we need to process the form data
  if request.method == 'POST':
      # create form instances and populate with data from the request
      push_form = PushForm(request.POST)
      token_form  = TokenForm(request.POST)

      # If it isn't, perhaps the pin is valid
      if token_form.is_valid():
        if perform_second_factor_pin(request.user, token_form.cleaned_data['token_code']):
          logger.debug('Second factor pin succeeded for %s' % request.user)
          # If authentication succeeded, log in is ok
          # return HttpResponse(request.session['saml_data'])
          print "second factor token worked"
        else:
          logger.debug("Second factor pin failed; %s will not be permitted to log in" % request.user)
          # Otherwise they should not be logging in.
          logout(request)
          # FIXME: return error text to user intead of generic 403
          raise PermissionDenied("Second authentication factor failed")

      # check if the push is valid
      elif push_form.is_valid():
        if perform_second_factor_push(request.user):
          logger.debug('Second factor push succeeded for %s' % request.user)
          # If authentication succeeded, log in is ok
          # return HttpResponse(request.session['saml_data'])
          print 'second factor push worked'
        else:
          logger.debug("Second factor push failed; %s will not be permitted to log in" % request.user)
          # Otherwise they should not be logging in.
          logout(request)
          # FIXME: return error text to user intead of generic 403
          raise PermissionDenied("Second authentication factor failed")

  # if a GET (or any other method) we'll create a blank form
  else:
      push_form = PushForm()
      token_form  = TokenForm()

  return render(request, display_template, {'formpush': push_form, 'formtoken': token_form})

