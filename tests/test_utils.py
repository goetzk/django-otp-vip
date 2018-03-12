# http://pytest-django.readthedocs.io/en/latest/database.html
import pytest

import requests
import requests_mock

import datetime
import pytz

from django.contrib.auth.models import User

# Import data fixtures
from .api_data import *

from otp_vip import utils
from otp_vip import models

import otp_vip.utils as dovu


# Test if timers have changed
def test_settings_sleep_seconds():
  assert dovu.VIP_POLL_SLEEP_SECONDS == 10

def test_settings_sleep_max_count():
  assert dovu.VIP_POLL_SLEEP_MAX_COUNT == 10

@requests_mock.mock()
def test_create_remote_vip_user_user_does_not_exist(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><CreateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>fd338241_bb56_418e_b245_a2e97e160515</requestId><status>0000</status><statusMessage>Success</statusMessage></CreateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': 'fd338241_bb56_418e_b245_a2e97e160515',\n    'status': '0000',\n    'statusMessage': 'Success',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.create_remote_vip_user('karl+testing-3@example.com')
    assert str(api_result) == response_json

@requests_mock.mock()
def test_create_remote_vip_user_user_already_exists(session_override):
    response_xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><CreateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>cad50a5a_ea65_4c78_b5e6_607b86d115c9</requestId><status>6002</status><statusMessage>User already exists.</statusMessage></CreateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': 'cad50a5a_ea65_4c78_b5e6_607b86d115c9',\n    'status': '6002',\n    'statusMessage': 'User already exists.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.create_remote_vip_user('karl+testing-3@example.com')
    assert str(api_result) == response_json


@requests_mock.mock()
def test_disable_remote_vip_user(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>3dd62c4c_405b_45c1_91ac_44bf84378149</requestId><status>0000</status><statusMessage>Success</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '3dd62c4c_405b_45c1_91ac_44bf84378149',\n    'status': '0000',\n    'statusMessage': 'Success',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.disable_remote_vip_user('karl@example.com')
    assert str(api_result) == response_json

@requests_mock.mock()
def test_disable_remote_vip_user_unknown_user(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>86ca05ef_61fd_47c4_a58b_afcfcd7398df</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '86ca05ef_61fd_47c4_a58b_afcfcd7398df',\n    'status': '6003',\n    'statusMessage': 'User does not exist.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.disable_remote_vip_user('karl+testing-2@example.com')
    assert str(api_result) == response_json


# FIXME: coverage is not marking the code tested here as checked.
@requests_mock.mock()
def test_rename_remote_vip_user(session_override):
  response_xml="""<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>ad4b9495_8ba0_445f_a7e7_14beb9829e2e</requestId><status>0000</status><statusMessage>Success</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
  response_json = {
    'requestId': 'ad4b9495_8ba0_445f_a7e7_14beb9829e2e',
    'status': '0000',
    'statusMessage': 'Success',
    'detail': None,
    'detailMessage': None
  }
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
  api_result = utils.rename_remote_vip_user('karl+testing-3@example.com', 'testing-again@example.com')
  assert sorted(api_result) == sorted(response_json)

@requests_mock.mock()
def test_query_user_info_user_exists(session_override):
    response_xml = get_user_info_credentials_xml()
    response_json = get_user_info_credentials_json()
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    result = utils.query_user_info('karl@example.com')
    assert sorted(result) == sorted(response_json)

# FIXME: For the life of me, can't see why this test isn't resulting in
# coverage for the relevant utils code - it is actually running the code!
@requests_mock.mock()
def test_query_user_info_user_does_not_exist(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><GetUserInfoResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>e656f6e2_c144_4e15_b56e_b14284b926e0</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></GetUserInfoResponse></S:Body></S:Envelope>"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    result = utils.query_user_info('missing@example.com')
    assert result == {}

# TODO: check if I also need to wrap these tests in mocks

@requests_mock.mock()
def test_create_remote_vip_user_user_does_not_exist(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><CreateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>fd338241_bb56_418e_b245_a2e97e160515</requestId><status>0000</status><statusMessage>Success</statusMessage></CreateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': 'fd338241_bb56_418e_b245_a2e97e160515',\n    'status': '0000',\n    'statusMessage': 'Success',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.create_remote_vip_user('karl+testing-3@example.com')
    assert str(api_result) == response_json

@requests_mock.mock()
def test_create_remote_vip_user_user_already_exists(session_override):
    response_xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><CreateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>cad50a5a_ea65_4c78_b5e6_607b86d115c9</requestId><status>6002</status><statusMessage>User already exists.</statusMessage></CreateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': 'cad50a5a_ea65_4c78_b5e6_607b86d115c9',\n    'status': '6002',\n    'statusMessage': 'User already exists.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.create_remote_vip_user('karl+testing-3@example.com')
    assert str(api_result) == response_json


@requests_mock.mock()
def test_disable_remote_vip_user(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>3dd62c4c_405b_45c1_91ac_44bf84378149</requestId><status>0000</status><statusMessage>Success</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '3dd62c4c_405b_45c1_91ac_44bf84378149',\n    'status': '0000',\n    'statusMessage': 'Success',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.disable_remote_vip_user('karl@example.com')
    assert str(api_result) == response_json

@requests_mock.mock()
def test_disable_remote_vip_user_unknown_user(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>86ca05ef_61fd_47c4_a58b_afcfcd7398df</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '86ca05ef_61fd_47c4_a58b_afcfcd7398df',\n    'status': '6003',\n    'statusMessage': 'User does not exist.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    api_result = utils.disable_remote_vip_user('karl+testing-2@example.com')
    assert str(api_result) == response_json


@requests_mock.mock()
def test_query_user_info_user_exists(session_override):
    response_xml = get_user_info_credentials_xml()
    response_json = get_user_info_credentials_json()
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    result = utils.query_user_info('karl@example.com')
    assert sorted(result) == sorted(response_json)

# Tests for adding credentials will be extensive, there are lots of permutations still to do:
# everything worked
# user, credential or friendly name missing / empty (Actually, this will be done by + tested in external validation)
# device already added (to this user, to another user if relevant)
# Something i forgot

@requests_mock.mock()
def test_add_credential_to_vip_unknown_user(session_override):
    response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AddCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>4b18fb48_1f53_4b0e_9485_d8b4a63fd6c4</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></AddCredentialResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '4b18fb48_1f53_4b0e_9485_d8b4a63fd6c4',\n    'status': '6003',\n    'statusMessage': 'User does not exist.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    result = utils.add_credential_to_vip('karl.unknown@example.com', 'SYMC21519954', 'Test device')
    assert str(result) == response_json

@requests_mock.mock()
def test_add_credential_to_vip_locked_user(session_override):
    response_xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AddCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>9a2207a0_1d44_44b7_aec1_1d88a3101009</requestId><status>601B</status><statusMessage>Operation not allowed in current user status.</statusMessage></AddCredentialResponse></S:Body></S:Envelope>"""
    response_json = """{\n    'requestId': '9a2207a0_1d44_44b7_aec1_1d88a3101009',\n    'status': '601B',\n    'statusMessage': 'Operation not allowed in current user status.',\n    'detail': None,\n    'detailMessage': None\n}"""
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
    result = utils.add_credential_to_vip('karl@example.com', 'SYMC21519954', 'Test device')
    assert str(result) == response_json

@requests_mock.mock()
def test_add_credential_to_vip_disabled_user(session_override):
  response_xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AddCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>84ab13f7_888b_402d_837b_4fcee2c91b4c</requestId><status>0000</status><statusMessage>Success</statusMessage></AddCredentialResponse></S:Body></S:Envelope>"""
  response_json = {
    'requestId': '84ab13f7_888b_402d_837b_4fcee2c91b4c',
    'status': '0000',
    'statusMessage': 'Success',
    'detail': None,
    'detailMessage': None
  }
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
  result = utils.add_credential_to_vip('testing-again@example.com', 'SYDC23459775', 'VIP Access for Mac v2')
  assert sorted(result) == sorted(response_json)

@requests_mock.mock()
def test_remove_credential_from_vip_successful_removal(session_override):
  """Successfully remove a registered credential from a user."""
  response_xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><RemoveCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>b24eb2b9_3685_441c_bc39_325d75a712fe</requestId><status>0000</status><statusMessage>Success</statusMessage></RemoveCredentialResponse></S:Body></S:Envelope>"""
  response_json = {
    'requestId': 'b24eb2b9_3685_441c_bc39_325d75a712fe',
    'status': '0000',
    'statusMessage': 'Success',
    'detail': None,
    'detailMessage': None
  }
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
  result = utils.remove_credential_from_vip('testing-again@example.com', 'SYDC23459775')
  assert sorted(result) == sorted(response_json)

@requests_mock.mock()
def test_remove_credential_from_vip_invalid_user(session_override):
  """Test behaviour when user does not exist in VIP."""
  response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><RemoveCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>fb2a1571_23e9_4b99_b426_13e763bd8949</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></RemoveCredentialResponse></S:Body></S:Envelope>"""
  response_json = {
    'requestId': 'fb2a1571_23e9_4b99_b426_13e763bd8949',
    'status': '6003',
    'statusMessage': 'User does not exist.',
    'detail': None,
    'detailMessage': None
  }
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
  result = utils.remove_credential_from_vip('fakeuser', 'SYMC21519954')
  assert sorted(result) == sorted(response_json)

@requests_mock.mock()
def test_remove_credential_from_vip_credential_not_bound_to_user(session_override):
  """Test behaviour when user does not use the supplied credential."""
  response_xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><RemoveCredentialResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>9291598d_e5d0_49ff_948e_60d9d1802d31</requestId><status>6007</status><statusMessage>No binding exists between user and credential.</statusMessage></RemoveCredentialResponse></S:Body></S:Envelope>"""
  response_json = {
    'requestId': '9291598d_e5d0_49ff_948e_60d9d1802d31',
    'status': '6007',
    'statusMessage': 'No binding exists between user and credential.',
    'detail': None,
    'detailMessage': None
  }
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/ManagementService_1_8', text=response_xml)
  result = utils.remove_credential_from_vip('testing-again@example.com', 'SYMC21519954')
  assert sorted(result) == sorted(response_json)

# @pytest.mark.django_db()
# def test_update_user_record_known_user_id_no_vipuser_record(get_user_info_no_credentials_json):
#   """Should be true if users details can be updated in DB.
# 
#   This covers creation of VipUser instance, the user in test has multiple accounts.
#   """
#   altered_api = get_user_info_no_credentials_json
#   altered_api['userId'] = 'karl+testing@example.com'
#   # Ensure user has no vipuser entry
#   for u in User.objects.filter(email=altered_api['userId']):
#     models.VipUser.objects.filter(user=u).delete()
#   assert utils.update_user_record(get_user_info_no_credentials_json) is True
# 
# @pytest.mark.django_db()
# def test_update_user_record_known_user_id(get_user_info_no_credentials_json):
#   """Should be true if users details can be updated in DB
# 
#   This covers creation of VipUser instance, the user in test has multiple accounts.
#   """
#   altered_api = get_user_info_no_credentials_json
#   altered_api['userId'] = 'karl+testing@example.com'
#   assert utils.update_user_record(get_user_info_no_credentials_json) is True
# 
# @pytest.mark.django_db()
# def test_update_user_record_unknown_user_id(get_user_info_credentials_json):
#   altered_api = get_user_info_credentials_json
#   altered_api['userId'] = 'unknown@example.com'
#   assert utils.update_user_record(altered_api) is False
# 
# def test_update_user_record_invalid_api_data():
#   """What happens if the api data is not a dictn. False is returned"""
#   assert utils.update_user_record('invalid data') is False
# 
# @pytest.mark.django_db()
# def test_update_user_record_date_no_timezone(get_user_info_no_credentials_json):
#   """What happens if the data supplied has no timezone. It should be coerced in to having one"""
#   altered_api = get_user_info_no_credentials_json
#   altered_api['userCreationTime'] = datetime.datetime.now()
#   altered_api['userId'] = 'foo@bar'
#   update_result = utils.update_user_record(altered_api)
#   # Ensure user has no vipuser entry
#   vip_user = models.VipUser.objects.get(user=User.objects.filter(email=altered_api['userId']))
#   assert vip_user.vip_created_at == altered_api['userCreationTime'].replace(tzinfo=pytz.utc)
# 
# @pytest.mark.django_db()
# def test_discover_user_from_email_nothing_supplied():
#   """If no email is passed return None"""
#   assert utils.discover_user_from_email('') is None
# 
# @pytest.mark.django_db()
# def test_discover_user_from_email_invalid_email():
#   """
#   numbers and other invalid text are caught by this test
#   """
#   assert utils.discover_user_from_email('i am not an email') is None
# 
# @pytest.mark.django_db()
# def test_discover_user_from_email_no_user():
#   """Trying to discover a user who doesn't exist returns None"""
#   assert utils.discover_user_from_email('karl+testing-discourse@example.com') is None
# 
# @pytest.mark.django_db()
# def test_discover_user_from_email_single_user():
#   """Ensure we have a User object returned when supplying the email of a valid user"""
#   assert isinstance(utils.discover_user_from_email('karl+testing@example.com'), User)
# 
# @pytest.mark.django_db()
# def test_discover_user_from_email_multiple_users():
#   """Ensure we have a User object returned when supplying the email of user with multiple accounts"""
#   assert isinstance(utils.discover_user_from_email('karl@example.com'), User)
# 
# 
# @pytest.mark.django_db()
# def test_validate_token_data_user_without_email():
#   """Ensure False is returned when user has no email address"""
#   assert utils.validate_token_data('', '123456') is False


def test_send_user_auth_push_missing_user():
  assert utils.send_user_auth_push('') is None

@requests_mock.mock()
def test_send_user_auth_push_unknown_user(session_override):
  response_xml = utils_send_user_auth_push_invalid_user_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert utils.send_user_auth_push('invalid user') is None

@requests_mock.mock()
def test_send_user_auth_push_user_has_no_credentials(session_override):
  response_xml = utils_send_user_auth_push_user_has_no_credentials()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert utils.send_user_auth_push('karl+testing@example.com') is None

@requests_mock.mock()
def test_send_user_auth_push_successful(session_override):
  response_xml = utils_send_user_auth_push_request_sent_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert len(utils.send_user_auth_push('karl+testing@example.com')) > 4
  assert utils.send_user_auth_push('karl+testing@example.com') is not None

# test for send_user_auth_push(invalid/unknown token code) -> return None.


def test_poll_user_auth_push_without_transaction_id():
  """False if no transaction id passed in"""
  assert utils.poll_user_auth_push('') is False

@requests_mock.mock()
def test_poll_user_auth_push_request_in_progress(session_override):
  response_xml = utils_poll_user_auth_push_in_progress_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
  utils.VIP_POLL_SLEEP_SECONDS = 1
  utils.VIP_POLL_SLEEP_MAX_COUNT = 1
  assert utils.poll_user_auth_push('2ae68a940ec4236b') is False

@requests_mock.mock()
def test_poll_user_auth_push_request_approved(session_override):
  response_xml = utils_poll_user_auth_push_user_approved_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
  assert utils.poll_user_auth_push('2ae68a940ec4236b') is True

@requests_mock.mock()
def test_poll_user_auth_push_request_denied(session_override):
  response_xml = utils_poll_user_auth_push_user_denied_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
  assert utils.poll_user_auth_push('0bd24cf0c94caefa') is False

@requests_mock.mock()
def test_poll_user_auth_push_unknown_transaction_id(session_override):
  """Return False if the Transaction ID is unknown.

  The following three classes of transaction fall in to this test:
    * Transaction IDs that are expired
    * Transaction IDs that are already used
    * Transaction IDs that are schema valid but made up lies

  Why? Because the API doesn't differentiate between them.
  """
  response_xml = utils_poll_user_auth_push_unknown_request_id()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
  # Everything over 4 characters is valid for the API, its just a question of being known
  assert utils.poll_user_auth_push('12345678') is False

# FIXME: Does not change test coverage, should test the Data Validation code path
@requests_mock.mock()
def test_poll_user_auth_push_invalid_data(session_override):
  response_xml = utils_poll_user_auth_push_unknown_request_id()
  # custom_response = response_xml.replace('<transactionId>23456</transactionId><status>7005</status>', '')
  custom_response = response_xml.replace('7005', '')
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=custom_response)
  assert utils.poll_user_auth_push('0bd24cf0c94caefa') is False

@requests_mock.mock()
def test_poll_user_auth_push_invalid_xml(session_override):
  response_xml = '<xml>that is invalid</xml>'
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
  assert utils.poll_user_auth_push('0bd24cf0c94caefa') is False



@requests_mock.mock()
def test_validate_token_data_successful(session_override):
  """Ensure False is returned when user has no vip associated"""
  response_xml = validate_token_data_successful_validation()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert utils.validate_token_data('karl@example.com', '905595') is True

@requests_mock.mock()
def test_validate_token_data_user_unknown_to_vip(session_override):
  """Ensure False is returned when user has no vip associated"""
  response_xml = validate_token_data_user_unknown_to_vip_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert utils.validate_token_data('testing@example.com', '123456') is False

@requests_mock.mock()
def test_validate_token_data_token_has_letter(session_override):
  """Ensure False is returned when token includes letter"""
  response_xml = validate_token_data_token_has_letter_xml()
  session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
  assert utils.validate_token_data('karl+testing@example.com', '12345k') is False

# @pytest.mark.django_db()
# @requests_mock.mock()
# def test_validate_token_data_token_has_9_digits(session_override):
#   """Ensure False is returned when token includes more than 6 digits (test uses 9)"""
#   response_xml = validate_token_data_code_too_long_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
#   assert utils.validate_token_data('karl+testing@example.com', '123456789') is False
# 
# 
# @requests_mock.mock()
# @pytest.mark.django_db()
# def test_validate_token_data_user_is_locked(session_override):
#   """Ensure False is returned when token includes letter"""
#   response_xml = validate_token_data_user_is_locked_xml()
#   session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8', text=response_xml)
#   assert utils.validate_token_data('karl@example.com', '12345k') is False


