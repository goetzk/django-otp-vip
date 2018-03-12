import pytest

import requests
import requests_mock

import datetime
import pytz

# Import data fixtures
from .api_data import *

from django.contrib.auth.models import User

from otp_vip import credential_models

# TODO: credential_models.update_user_credentials is a big and complicated function, it will need more tests.

def test_update_user_credentials_receives_empty_string():
  """If no data is passed to update_user_credentials it should return True as
  there is nothing to update.
  """
  assert credential_models.update_user_credentials('') is False

def test_update_user_credentials_receives_empty_list():
  """If no data is passed to update_user_credentials it should return True as
  there is nothing to update.
  """
  assert credential_models.update_user_credentials([]) is False

# @pytest.mark.django_db()
# def test_update_user_credentials_api_without_credentials(get_user_info_no_credentials_json):
#   """Some API calls don't return credentialBindingDetail, return True if we have
#   been given one of them.
#   """
#   assert credential_models.update_user_credentials(get_user_info_no_credentials_json) is True

# @pytest.mark.django_db()
# def test_update_user_credentials_unknown_user_id(get_user_info_credentials_json):
#   """If the userId returned by API isn't known to us return false - this user
#   requires further investigation
#   """
#   altered_api = get_user_info_credentials_json
#   altered_api['userId'] = 'unknown@example.com'
#   assert credential_models.update_user_credentials(altered_api) is False

# @pytest.mark.django_db()
# def test_update_user_credentials_push_attributes_recorded(get_user_info_credentials_json):
#   """Ensure the push attribute of push capable devices are recorded."""
#   # We only have one credential in this test data
#   first_cred = get_user_info_credentials_json['credentialBindingDetail'][0]
# 
#   run_result = credential_models.update_user_credentials(get_user_info_credentials_json)
#   cred_db = credential_models.VipPushCredential.objects.get(credential_id = first_cred['credentialId'])
#   assert cred_db.push_enabled is True
#   assert str(cred_db.attribute_platform) == 'ANDROID'
# 
# @pytest.mark.django_db()
# def test_update_user_credentials_token_credential_created(get_user_info_credentials_json):
#   """Ensure token style credential is created if the credential doesn't have push attributes.
#   """
#   # The first credential in this test data has no pushAttributes so we delete the others and use that.
#   altered_api = get_user_info_credentials_multiple_credentials_json()
#   first_cred = altered_api['credentialBindingDetail'][0]
#   altered_api['credentialBindingDetail'] = [first_cred]
# 
#   run_result = credential_models.update_user_credentials(altered_api)
#   cred_db = credential_models.VipTokenCredential.objects.get(credential_id = first_cred['credentialId'])
#   assert cred_db.push_enabled is False
# 
# @pytest.mark.django_db()
# def test_update_user_credentials_all_credentials_created(get_user_info_credentials_multiple_credentials_json):
#   """Ensure all credentials in a list are created in DB."""
#   # Create db records, gather result
#   run_result = credential_models.update_user_credentials(get_user_info_credentials_multiple_credentials_json)
# 
#   # If these succeed the devices were created and have the correct push'ness'
#   assert run_result is True
#   # These two are the same token, a push capable Android device
#   assert credential_models.VipPushCredential.objects.get(credential_id = 'SYMC21519954')
#   assert credential_models.VipTokenCredential.objects.get(credential_id = 'SYMC21519954')
#   # These two are VIP Access for Mac (versions 1 and 2 respectively)
#   assert credential_models.VipTokenCredential.objects.get(credential_id = 'VSST43994978')
#   assert credential_models.VipTokenCredential.objects.get(credential_id = 'SYDC23459775')
# 
# def test_update_user_credentials_invalid_api_data():
#   """What happens if the api data is not a dictn. False is returned"""
#   assert credential_models.update_user_credentials('invalid data') is False
# 
# 
# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_vip_push_credential_generate_challenge_successful_transaction(session_override):
#   """Response when generate_challenge successful records tranaaction id"""
#   response_xml_auth = utils_send_user_auth_push_request_sent_xml()
#   response_xml_query = utils_poll_user_auth_push_user_approved_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml_auth)
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml_query)
#   # I know this from recording the XML and the code to auto detect it would add complexity.
#   response_transaction_id = '2ae68a940ec4236b'
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   output = vpc.generate_challenge()
#   assert output == 'Sent (Check your device).'
#   assert vpc.latest_transaction_id == response_transaction_id
# 
# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_vip_push_credential_generate_challenge_no_transaction(session_override):
#   """Check response when generate_challenge does not return a transaction id"""
#   response_xml = utils_send_user_auth_push_request_sent_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
#   # I know this from recording the XML and the code to auto detect it would add complexity.
#   response_transaction_id = '2ae68a940ec4236b'
#   # Other option would be choosing to return 'bad' response_xml
#   u = User.objects.get(username='admin')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   output = vpc.generate_challenge()
#   assert output == 'An error occurred trying to send the push'
# 
# 
# 
# @pytest.mark.django_db()
# def test_vip_push_credential_verify_token_check_for_params():
#   """If unexpected argument return False"""
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   vpc.save()
#   assert vpc.verify_token('unexpected argument') is False
# 
# @pytest.mark.django_db()
# def test_vip_push_credential_verify_token_transaction_id_exists():
#   """If no transaction id return false"""
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   vpc.save()
#   assert vpc.verify_token() is False
# 
# 
# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_vip_push_credential_verify_token_successful_validation(session_override):
#   """Successful (user accpeted) push"""
#   response_xml = utils_poll_user_auth_push_user_approved_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   # I know this from recording the XML and the code to auto detect it would add complexity.
#   vpc.latest_transaction_id = '2ae68a940ec4236b'
#   vpc.POLL_SLEEP_SECONDS = 1
#   assert vpc.verify_token() is True
# 
# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_vip_push_credential_verify_token_unsuccessful_validation(session_override):
#   """Failed (user denied) push"""
#   response_xml = utils_poll_user_auth_push_user_denied_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipPushCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   # I know this from recording the XML and the code to auto detect it would add complexity.
#   vpc.latest_transaction_id = '0bd24cf0c94caefa'
#   vpc.POLL_SLEEP_SECONDS = 1
#   assert vpc.verify_token() is False
# 
# 
# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_vip_token_credential_verify_token_successful_validation(session_override):
#   """Successfully validate token supplied by user.
# 
#   This doesn't need to be a successful validation - verify_token has no
#   internal error handling - but it 'feel nice' for it to be one.
#   validate_token calls validate_token_data(), which has comprehensive tests in
#   test_utils.py
#   """
#   response_xml = validate_token_data_successful_validation()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
#   u = User.objects.get(email='karl@example.com')
#   vpc = credential_models.VipTokenCredential.objects.create(user = u,
#                    token_expiration_date = datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(days=365), # Somewhere in the future
#                    bind_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=60), # Somewhere before update/authn
#                    token_last_update = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    last_authn_time = datetime.datetime.now().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30), # Somewhere in the past
#                    )
#   # I know this from recording the XML and the code to auto detect it would add complexity.
#   assert vpc.verify_token('905595') is True

