# -*- coding: utf-8 -*-
"""Custom views for VIP.

These views aim to aid in deploying a VIP compatible app.
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from django_otp_vip.credential_models import send_user_auth_push, poll_user_auth_push

from django_otp_vip.forms import PushForm, TokenForm

from django_otp_vip.utils import update_vip_user_records

from django_otp.forms import OTPTokenForm

import logging
logger = logging.getLogger(__name__)

@login_required
def run_otp(request, display_template='django_otp_vip/validate_vip.html'):
  """Perform second factor.

  This function is to perform 'other' user validation, for example 2nd factor
  checks. Override this view per the documentation if using this functionality.
  """
  logger.debug('In run_otp view')

  # Update known details about user including credentials
  try:
    logger.debug('Attempting to update user details')
    full_user_details = query_user_info(request.user.email)
    if not full_user_details:
      print('user does not exist, logging of error will occur later')
      return False
    updated_records = update_vip_user_records(full_user_details)
  except Exception as ee:
    # handle this better....
    updated_records = None
    print 'balalhasdlhfaldfh'
    print ee

  if updated_records:
    print "The records were updated"
    # check the return code is success
    # that we have a user
    # that they have >= 1 credential to validate with
    pass

  # if this is a POST request we need to process the form data
  if request.method == 'POST':
      logger.debug('post method')

      # create form instances and populate with data from the request
      # https://stackoverflow.com/a/20802107
      # https://github.com/malept/pyoath-toolkit/blob/master/examples/django/example/views.py#L116
      push_form = PushForm(request.user, request, data=request.POST)
      token_form  = TokenForm(request.user, request, data=request.POST)

      logger.debug(request.POST)

      logger.debug('are either forms valid?')

      # check if token is valid
#       if token_form.is_valid():
#         logger.debug('second factor token worked')
#         return HttpResponse('/')
#       else:
#         logger.debug('token form errors')
#         logger.debug(token_form.errors.as_data())

      # check if the push is valid
      if push_form.is_valid():
        logger.debug('second factor push worked')
        return HttpResponse('push worked')
#       else:
#         logger.debug('push form errors')
#         logger.debug(push_form.errors.as_data())

  # if a GET (or any other method) we'll create a blank form
  else:
      logger.debug('creating some empty forms')
      # if some push credentials are available, show form. Otherwise don't show.
      push_form = PushForm(request.user)
      # ditto token credentials
      token_form  = TokenForm(request.user)

  # TODO: check if there are devices that will work with the two types of forms and if not set None
 #  return render(request, display_template, {'formpush': push_form, 'formtoken': token_form })
  return render(request, display_template, {'formpush': push_form })

