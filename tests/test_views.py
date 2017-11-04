# http://pytest-django.readthedocs.io/en/latest/helpers.html#rf-requestfactory

import pytest

# Import data fixtures
from .api_data import *

from otp_vip import views

from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User


def test_update_vip_user_records_invalid_data():
  """What happens if the api data is not a dict. False is returned"""
  assert views.update_vip_user_records('invalid data') is False


# @pytest.mark.django_db()
# def test_update_vip_user_records(get_user_info_credentials_json):
#   """Return true if valid API data is passed in."""
#   assert views.update_vip_user_records(get_user_info_credentials_json) is True
# 
# @pytest.mark.django_db()
# def test_update_vip_user_records_user_does_not_exist_locally(get_user_info_credentials_json):
#   """Failure in one of the sub utilities should cause this to return False.
# 
#   If the userId returned by API isn't known one of update_user_credentials
#   or update_user_record should fail.
#   This was directly baased on a test for update_user_credentials
#   """
#   altered_api = get_user_info_credentials_json
#   altered_api['userId'] = 'unknown@example.com'
#   assert views.update_vip_user_records(altered_api) is False


# @pytest.mark.django_db()
# def test_run_multi_factor_check_with_plain_user(rf):
#   # Create and configure request
#   request = rf.get(reverse('run_multifactor_requirement'))
#   request.user = User.objects.get(username='test_user')
#
#   # Then use it to generate a response
#   response = views.multi_factor_check(request)
#   assert response.status_code == 200

# FIXME: add session to request so logout() can succeed.
# FIXME: handle PermissionDenied as raised on failed login
# @pytest.mark.django_db()
# def test_otp_post_with_no_valid_token_plain_user(rf):
#   # Create and configure request
#   request = rf.post(reverse('run_multi_factor'))
#   request.user = User.objects.get(username='test_user')
#
#   # Then use it to generate a response
#   response = views.multi_factor(request)
#   assert response.status_code == 403


# FIXME: need to modify rf to include form data
# @pytest.mark.django_db()
# def test_multi_factor_token_form_valid_second_factor_succeeded(rf):
#   """
#   posted form was valid and second factor auth succeeded.
#   """
#   request = rf.post(reverse('run_multi_factor'))
#   request.user = User.objects.get(username='test_user')
#
#   # Then use it to generate a response
#   response = views.multi_factor(request)
#   assert response.status_code == 200

# NOTE: these tests might not be needed, see comment in views.multi_factor
# @pytest.mark.django_db()
# def test_multi_factor_token_form_valid_second_factor_failed(rf):
#   """
#   posted form valid, second factor auth failed.
#   """

# @pytest.mark.django_db()
# def test_multi_factor_push_form_valid_second_factor_succeeded(rf):
#   """
#   posted form was valid and second factor auth succeeded.
#   """
#
# @pytest.mark.django_db()
# def test_multi_factor_push_form_valid_second_factor_failed(rf):
#   """
#   posted form valid, second factor auth failed.
#   """

# @pytest.mark.django_db()
# def test_multi_factor_get_page(rf):
#   """Load page to fill in form.
# 
#   User is logged in.
#   """
#   request = rf.get(reverse('run_multi_factor'))
#   request.user = User.objects.get(username='test_user')
# 
#   # Then use it to generate a response
#   response = views.multi_factor(request)
#   assert response.status_code == 200

# @pytest.mark.django_db()
# def test_multi_factor_get_page_not_logged_in(rf):
#   """Load page to fill in form.
#
#   User is not logged in.
#   """
#   request = rf.get(reverse('run_multi_factor'))
#   request.user = User.objects.get(username='test_user')
#
#   # Then use it to generate a response
#   response = views.multi_factor(request)
#   assert response.status_code == 302


# @pytest.mark.django_db()
# def test_manage_two_factor(rf):
#   """Does my vip render for a logged in user."""
#   request = rf.get(reverse(''))
#   request.user = User.objects.get(username='pro_user')
#
#   # Then use it to generate a response
#   response = views.manage_two_factor(request)
#   assert response.status_code == 200

# FIXME
# @pytest.mark.django_db()
# def test_manage_two_factor_logged_in(rf):
#   request = rf.post(reverse(''))
#   request.user = User.objects.get(username='pro_user')
#
#   # Then use it to generate a response
#   response = views.manage_two_factor(request)
#   assert response.status_code == 200

