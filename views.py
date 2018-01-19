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

from django_otp.decorators import otp_required

from otp_vip import forms

from otp_vip import utils
from otp_vip import credential_models

from django_otp.forms import OTPTokenForm

import logging
logger = logging.getLogger(__name__)

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

#
# @login_required
# # name is 'run_multifactor_requirement'
# # Note: This could be removed if moving to 'user has credential == user wants
# # 2fa'. This allows for there to be a credential but no 2fa
# # https://github.com/lins05/django-otp/blob/7c152ba56b3fcca6b68adfbef192a25b3ed8245f/django-otp/django_otp/decorators.py
# # It may be worth customising the decorator to eliminate this view?
# def multi_factor_check(request, multifactor_redirect = 'login',
#                                   direct_redirect = '/', *args, **kwargs):
#   """Determine if a user is able to use multiple factors.
#
#   Once the check has been performed, redirect user to appropriate page.
#   """
#   logger.debug("in multi_factor_check")
#
#   if utils.should_user_multifactor(request.user):
#     logger.debug("Redirecting to multi factor page")
#     return HttpResponseRedirect(multifactor_redirect)
#   else:
#     logger.debug("No multi factor, redirecting to MyITPA")
#     return HttpResponseRedirect(direct_redirect)


@login_required
# Name is 'run_multi_factor'
def multi_factor(request, display_template='otp_vip/validate_vip.html'):
  """Perform second factor.

  This function is to perform 'other' user validation, for example 2nd factor
  checks. Override this view per the documentation if using this functionality.
  """
  logger.debug('In multi_factor view')
  display_template = 'otp_vip/validate_vip.html'
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

  return render(request, display_template, {'formpush': push_form, 'formtoken': token_form })


@login_required
@otp_required(if_configured=True)
def manage_two_factor(request, template=None):
  """Stub credential management page for users.

  This is a basic page to 'get things going', its expected to be replaced by
  something nicer per site.
  Template needs to be supplied
  """
  add_vip_token_credentials = None
  remove_vip_credentials = None
  users_vip_record = models.VipUser.objects.get(user=request.user)

  # Only process posts if _something_ was included (CSRF token is always included)
  if request.method == "POST" and len(request.POST) > 1:
    if request.POST.has_key('credential_id') or request.POST.has_key('name'):
      print 'credential_id code path' # string
      add_vip_token_credentials = forms.AddTokenCredential(request.POST)
      if add_vip_token_credentials.is_valid():
        added_cred = utils.add_credential_to_vip(request.user.email,
                                                add_vip_token_credentials.cleaned_data['credential_id'],
                                                add_vip_token_credentials.cleaned_data['name'],)
        if not added_cred.status == '0000':
          add_vip_token_credentials.add_error(None, 'An error occurred ({1} - {0}) while adding {2} via the API.'.format(added_cred.statusMessage, added_cred.status, add_vip_token_credentials.cleaned_data['credential_id']))
        # Attempt to update the DB based on API data now they have changed their tokens
        user_record_updated = utils.update_user_record(utils.query_user_info(request.user.email))
        token_credential_updated = credential_models.update_user_credentials(utils.query_user_info(request.user.email))

    if request.POST.has_key('credentials_list'):
      print 'credentials_list'
      remove_vip_credentials = forms.RemoveCredentials(request.POST, user = request.user)
      if remove_vip_credentials.is_valid():
        for removing_device in remove_vip_credentials.cleaned_data['credentials_list']:
          print 'removing %s' % removing_device
          # Remove single credential
          removed_cred = utils.remove_credential_from_vip(request.user.email, removing_device.credential_id)
          if not removed_cred.status == '0000':
            remove_vip_credentials.add_error(None, 'An error occurred ({1} - {0}) while removing {2} from {3} via the API.'.format(removed_cred.statusMessage, removed_cred.status, removing_device.credential_id, request.user.email ))
          else:
            # Only remove from DB if successfully removed from API.
            # update db with new credential data, including removing this one
            token_credential_updated = credential_models.update_user_credentials(utils.query_user_info(request.user.email))

  if not add_vip_token_credentials:
    add_vip_token_credentials = forms.AddTokenCredential()
  if not remove_vip_credentials:
    remove_vip_credentials = forms.RemoveCredentials(user = request.user)

# TODO: include update_vip_user_records here?

  return render(request, template, { 'remove_credentials': remove_vip_credentials,
                                              'add_token_credentials': add_vip_token_credentials,
                                              })


