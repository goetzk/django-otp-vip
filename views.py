# -*- coding: utf-8 -*-
"""Custom views for VIP.

These views aim to aid in deploying a VIP compatible app.
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.core.exceptions import PermissionDenied

from django_otp_vip.forms import PushForm, TokenForm

from django_otp_vip import utils
from django_otp_vip import credential_models

from django_otp.forms import OTPTokenForm

import logging
logger = logging.getLogger(__name__)

# TODO: merge this code in
def update_vip_user_records(info_from_api):
  """Update both user and credential DB records.

  This accepts output from query_user_info()
  """
  # Update the users "personal information"
  user_result = utils.update_user_record(info_from_api)

  # Update all credential records in DB
  credential_result = credential_models.update_user_credentials(info_from_api)

  if user_result and credential_result:
    return True

  return False


@login_required
# name is 'run_multifactor_requirement'
# Note: This could be removed if moving to 'user has credential == user wants
# 2fa'. This allows for there to be a credential but no 2fa
# https://github.com/lins05/django-otp/blob/7c152ba56b3fcca6b68adfbef192a25b3ed8245f/django-otp/django_otp/decorators.py
# It may be worth customising the decorator to eliminate this view?
def multi_factor_check(request, multifactor_redirect = 'login',
                                  direct_redirect = '/', *args, **kwargs):
  """Determine if a user is able to use multiple factors.

  Once the check has been performed, redirect user to appropriate page.
  """
  logger.debug("in multi_factor_check")

  if utils.should_user_multifactor(request.user):
    logger.debug("Redirecting to multi factor page")
    return HttpResponseRedirect(multifactor_redirect)
  else:
    logger.debug("No multi factor, redirecting to MyITPA")
    return HttpResponseRedirect(direct_redirect)


@login_required
# Name is 'run_multi_factor'
def multi_factor(request, display_template='django_otp_vip/validate_vip.html'):
  """Perform second factor.

  This function is to perform 'other' user validation, for example 2nd factor
  checks. Override this view per the documentation if using this functionality.
  """
  logger.debug('In multi_factor view')
  # todo: display template which includes symantec stuff but isn't exclusively symantec
  # display_template = 'itpa/my_itpa.html'
  display_template = 'django_otp_vip/validate_vip.html'
  logger.debug('using template {0}'.format(display_template))

  # if this is a POST request we need to process the form data
  if request.method == 'POST':
      logger.debug('post method')

      # create form instances and populate with data from the request
      # https://stackoverflow.com/a/20802107
      # https://github.com/malept/pyoath-toolkit/blob/master/examples/django/example/views.py#L116
      push_form = PushForm(request.user, request, data=request.POST)
      token_form  = TokenForm(request.user, request)

      logger.debug(request.POST)

      logger.debug('are either forms valid?')

      # check if token is valid
      if token_form.is_valid():
        # If authentication succeeded, log in is ok
        logger.debug('second factor token worked')
        return HttpResponse('/')
      else:
        logger.debug("Second factor pin failed; %s will not be permitted to log in" % request.user)
        # Otherwise they should not be logging in.
        logout(request)
        # FIXME: return error text to user instead of generic 403
        raise PermissionDenied("Second authentication factor failed")

      # check if the push is valid
      if push_form.is_valid():
        logger.debug('second factor push worked')
        return HttpResponse('push worked')
#       else:
#         logger.debug('push form errors')
#         logger.debug(push_form.errors.as_data())

  # if a GET (or any other method) we'll create a blank form
  else:

    logger.debug('Attempting to update user details')
    full_user_details = utils.query_user_info(request.user.email)

    if update_vip_user_records(full_user_details):
      logger.debug("Records for {0} were updated".format(request.user))
    else:
      logger.debug('Unable to update records for {0}'.format(request.user))

    logger.debug('creating some empty forms')
    # if some push credentials are available, show form. Otherwise don't show.
    push_form = PushForm(request.user)
    # ditto token credentials
    token_form  = TokenForm(request.user)

  # TODO: check if there are devices that will work with the two types of forms and if not set None
  return render(request, display_template, {'formpush': push_form, 'formtoken': token_form })

