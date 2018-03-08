# -*- coding: utf-8 -*-
"""Custom views for VIP.

These views aim to aid in deploying a VIP compatible app.
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.core.exceptions import PermissionDenied

from django_otp.decorators import otp_required
from django_otp import _handle_auth_login

import requests

from otp_vip import forms

from otp_vip import utils
from otp_vip import credential_models
from otp_vip import models

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


# Name is 'run_multi_factor'
@login_required
def multi_factor(request, display_template='otp_vip/validate_vip.html'):
  """Perform second factor.

  This function is to perform 'other' user validation, for example 2nd factor
  checks. Override this view per the documentation if using this functionality.
  """
  logger.debug('In multi_factor view')
  display_template = 'otp_vip/validate_vip.html'

  # if this is a POST request we need to process the form data
  if request.method == 'POST':
      # This should always exist as we set it via our template.
      final_destination = request.POST.get('next')

      # create form instances and populate with data from the request
      # https://stackoverflow.com/a/20802107
      # https://github.com/malept/pyoath-toolkit/blob/master/examples/django/example/views.py#L116
      push_form = forms.PushForm(request.user, request, data=request.POST)
      token_form  = forms.TokenForm(request.user, request, data=request.POST)

      logger.debug(request.POST)

      # If a token code is provided check if token is valid
      if request.POST.get('otp_token'):
        logger.debug("attempting to log in via pin")
        if token_form.is_valid():
          logger.debug('Second factor token worked using {0}'.format(request.user.otp_device))
          # Persist login using same method as used by upstreams user_logged_in signal handler
          _handle_auth_login('', request, request.user)
          return HttpResponseRedirect(final_destination)
        else:
          logger.debug("Second factor pin failed; %s will not be permitted to log in" % request.user)
          # Otherwise they should not be logging in.
          deny_login = True

      # If we don't have a token assume its a push, so check if the push is valid
      elif push_form.is_valid():
        logger.debug('second factor push worked using {0}'.format(request.user.otp_device))
        # Persist login using same method as used by upstreams user_logged_in signal handler
        _handle_auth_login('', request, request.user)
        return HttpResponseRedirect(final_destination)
      else:
        deny_login = True
        logger.debug('Neither auth succeeded')
        if token_form.errors:
          logger.debug('Token form errors')
          logger.debug(token_form.errors.as_data())
        if push_form.errors:
          logger.debug('Push form errors')
          logger.debug(push_form.errors.as_data())

      if deny_login:
        # logout(request)
        raise PermissionDenied("Second authentication factor failed")

  # If a GET (or any other method) we'll create a blank form
  else:
    # 'next' is only available via GET, if we want it in our POST data we need
    # to add it here.
    if request.GET.get('next'):
      going_to = request.GET.get('next')
    # This plays second fiddle to request[next] because it might be left over
    # from an earlier log in but they will always want next to be, uh, next.
    # When chained login -> otp -> result that is impossible, but when otp is
    # only required for subsets of a site this will be needed.
    elif request.session['final_destination']:
      going_to = request.session.get('final_destination')
    else:
      going_to = '/myitpa/'


    logger.debug('Attempting to update user details')
    full_user_details = utils.query_user_info(request.user.email)

    if update_vip_user_records(full_user_details):
      logger.debug("Records for {0} were updated".format(request.user))
    else:
      logger.debug('Unable to update records for {0}'.format(request.user))

    logger.debug('creating some empty forms')
    # if some push credentials are available, show form. Otherwise don't show.
    push_form = forms.PushForm(request.user)
    # ditto token credentials
    token_form  = forms.TokenForm(request.user)

  return render(request, display_template, {'formpush': push_form, 'formtoken': token_form, 'going_to': going_to })


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
  try:
    users_vip_record = models.VipUser.objects.get(user=request.user)
  except models.VipUser.DoesNotExist as dne:
    logger.debug('{0} does not have a VipUser object. Are they permitted here?'.format(request.user))
    raise Http404

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
      remove_vip_credentials = forms.RemoveCredentials(request.POST, user = request.user)
      if remove_vip_credentials.is_valid():
        for removing_device in remove_vip_credentials.cleaned_data['credentials_list']:
          logger.debug('removing {0}'.format(removing_device))
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

@login_required
@otp_required(if_configured=True)
def check_verification(request):
  """Stub view so we can run otp_required with if_configured=True.

  Django-OTP doesn't support an optional second factor login (like
  if_configured=True) for its authentication forms. Because of this, the
  suggested work around is to handle it in a separate view - for us, this is
  the view.

  So this should be used when you want people with otp configured to always use
  it, and those without it configured to never use it.

  As you can see from the code, request.session['final_destination'] is assumed
  to exist - I am using it to store the value of request.GET.get('next') so I can
  use it through multiple views.
  """
  # All multi factor magic is done via @otp_required then we log they're done and redirect.
  redirect_destination = request.session.get('final_destination', u'/')

  logger.debug('Redirecting {0} to {1}'.format(request.user, redirect_destination))

  return HttpResponseRedirect(redirect_destination)

