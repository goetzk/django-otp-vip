# for inspiration
# http://test-driven-django-development.readthedocs.io/en/latest/05-forms.html
# https://micropyramid.com/blog/django-unit-test-cases-with-forms-and-views/ (not reviewed yet)

 # https://stackoverflow.com/questions/42284947/basic-django-pytest-tests

import pytest

from django.contrib.auth.models import User

from otp_vip.models import VipUser
from datetime import datetime
import pytz

from otp_vip import forms
from otp_vip import credential_models


# @pytest.mark.django_db()
# def test_token_form_user_without_devices():
#   u = User.objects.get(username='admin')
#   tf = forms.TokenForm(u)
#   assert tf.is_valid() is False
#   assert tf.device_choices(u) == []
# 
# @pytest.mark.django_db()
# def test_token_form_user_with_devices():
#   u = User.objects.get(email='karl@example.com')
#   tf = forms.TokenForm(u)
#   assert tf.is_valid() is False
#   assert tf.device_choices(u) != []
# 
# 
# @pytest.mark.django_db()
# def test_push_form_user_without_devices():
#   u = User.objects.get(username='admin')
#   pf = forms.PushForm(u)
#   assert pf.is_valid() is False
#   assert pf.device_choices(u) == []
# 
# @pytest.mark.django_db()
# def test_push_form_user_with_devices():
#   u = User.objects.get(email='karl@example.com')
#   pf = forms.PushForm(u)
#   assert pf.is_valid() is False
#   assert pf.device_choices(u) != []
# 
# 
# @pytest.mark.django_db()
# def test_add_token_credential_valid_credential():
#   x = forms.AddTokenCredential( { 'name': 'test token', 'credential_id': 'SYDC23459775' })
#   assert x.is_valid() is True

# Zeep picks up the missing user and raises an exception.
# E               ValidationError: Missing element userId (AddCredentialRequest.userId)
# def test_add_token_credential_missing_user_valid_credential():
#   x = forms.AddTokenCredential( { 'name': 'test token', 'credential_id': 'SYDC23459775' } )
#   assert x.is_valid() is False

def test_add_token_credential_invalid_credential_too_short():
  x = forms.AddTokenCredential( { 'name': 'test token', 'credential_id': '12' })
  assert x.is_valid() is False

def test_add_token_credential_invalid_credential_bad_chars():
  x = forms.AddTokenCredential( { 'name': 'test token', 'credential_id': '1(*&^%$2' })
  assert x.is_valid() is False


# NOTE: It may be that credential values in the list below are the NAME not the ID.
# @pytest.mark.django_db()
# def test_remove_credentials_empty_credentials_list():
#   x = forms.RemoveCredentials({'credentials_list': [] }, user = User.objects.get(email='karl@example.com' ))
#   assert x.is_valid() is False
# 
# @pytest.mark.django_db()
# def test_remove_credentials_invalid_credentials():
#   """Credentials which aren't in the list of possible credentials to remove."""
#   x = forms.RemoveCredentials({'credentials_list': ['ts', 'long-but-invalid'] }, user = User.objects.get(email='karl@example.com' ))
#   assert x.is_valid() is False

# This isn't testing the lines it is supposed to (143-149). I suspect I'm passing invalid data
# Or the DB doesn't have nexus in it at the time I'm trying to remove it.
# @pytest.mark.django_db()
# def test_remove_credentials_valid_length_but_invalid_credentials():
#   """Credentials which aren't in the list of possible credentials to remove.
#
#   This codepath is a problem because it requires a valid credential (in the DB)
#   to activate it, but we can only test the error path without allowing a real
#   credential to be removed from the api.
#   """
#   x = forms.RemoveCredentials({'credentials_list': [u'nexus'] }, user = User.objects.get(email='karl@example.com' ))
#   assert x.is_valid() is False

# def test_remove_credentials_removes_selected_credential()
#   """Actually remove a credential."""

