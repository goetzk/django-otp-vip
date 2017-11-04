"""Test API calls with Symantec.

API calls are tested transitively via whatever is calling them - these helpers
simply make the calls nicer to work with so don't do anything to test in
themselves.

Most tests in this area are helpers or specific behaviours that were hard to
test via transitive testing.
"""

import requests
import requests_mock

from otp_vip import api

import datetime
import pytz

# Import data fixtures
from .api_data import *


def test_make_request_id_return_length():
  "Has something been returned"""
  assert len(api.make_request_id()) > 0

def test_make_request_id_dash():
  """Ensure output does not contain dash"""
  assert '-' not in api.make_request_id()

def test_make_request_id_return_type():
  "Has something been returned"""
  assert api.make_request_id() is not None

@requests_mock.mock()
def test_get_user_info_user_exists(session_override):
    response_xml = get_user_info_no_credentials_xml()
    response_json = get_user_info_no_credentials_json()
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    api_result = api.get_user_info(user_id = 'karl+testing@example.com')
    assert sorted(api_result) == sorted(response_json)


# See https://github.com/mvantellingen/python-zeep/issues/637
@requests_mock.mock()
def test_get_user_info_user_exists_with_token(session_override):
    response_xml = get_user_info_credentials_xml()
    response_json = get_user_info_credentials_json()
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    api_result = api.get_user_info(user_id = 'karl@example.com')
    assert sorted(api_result) == sorted(response_json)

@requests_mock.mock()
def test_get_user_info_user_does_not_exist(session_override):
    response_xml = get_user_info_user_does_not_exist_xml()
    response_json = get_user_info_user_does_not_exist_json()
    session_override.post('https://userservices-auth.vip.symantec.com/vipuserservices/QueryService_1_8', text=response_xml)
    api_result = api.get_user_info(user_id = 'does-not-exist@example.com')
    assert sorted(api_result) == sorted(response_json)

