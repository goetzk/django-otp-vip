"""API output from Symantec VIP.

There are several variables 'preloaded' with API data which can be used in
tests for various purposes.

I want to inject several large chunks of text in to several tests. I tried
adding it to the environment but that Didn't Work. Instead, these functions
return the required dicts.
https://stackoverflow.com/a/44702483
https://stackoverflow.com/a/22793013
"""

import pytest

import datetime
import pytz

@pytest.fixture
def get_user_info_credentials_xml():
  """XML response from API.

  This data is the XML version of that stored in the equivalently named _json
  fixture.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><GetUserInfoResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>7229df6c_4b86_4aa3_bfe4_7f07fe6c52c4</requestId><status>0000</status><statusMessage>Success</statusMessage><userId>karl@example.com</userId><userCreationTime>2017-08-15T01:15:14.555Z</userCreationTime><userStatus>LOCKED</userStatus><numBindings>1</numBindings><credentialBindingDetail><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType><credentialStatus>ENABLED</credentialStatus><tokenCategoryDetails><CategoryId>70</CategoryId><FormFactor>MOBILE</FormFactor><MovingFactor>TIME</MovingFactor><OtpGeneratedBy>SOFTWARE</OtpGeneratedBy></tokenCategoryDetails><tokenInfo><TokenId>SYMC21519954</TokenId><TokenKind>SOFTWARE</TokenKind><Adapter>OATH_TIME</Adapter><TokenStatus>ENABLED</TokenStatus><ExpirationDate>2038-01-01T00:00:00.205Z</ExpirationDate><LastUpdate>2017-11-09T02:13:00.000Z</LastUpdate><Owner>false</Owner></tokenInfo><bindingDetail><bindStatus>ENABLED</bindStatus><friendlyName>nexus</friendlyName><lastBindTime>2017-08-17T02:37:51.909Z</lastBindTime><lastAuthnTime>2017-11-09T02:13:00.022Z</lastAuthnTime><lastAuthnId>7CE4BB604887BEAD</lastAuthnId></bindingDetail><pushAttributes><Key>BIO_FINGERPRINT_CAPABLE</Key><Value>false</Value></pushAttributes><pushAttributes><Key>PUSH_PLATFORM</Key><Value>ANDROID</Value></pushAttributes><pushAttributes><Key>PUSH_ENABLED</Key><Value>true</Value></pushAttributes><pushAttributes><Key>BIO_FINGERPRINT_ENABLED</Key><Value>false</Value></pushAttributes><pushAttributes><Key>FIRST_FACTOR_CAPABLE</Key><Value>true</Value></pushAttributes></credentialBindingDetail></GetUserInfoResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def get_user_info_credentials_json():
  """Return full API output from a user's get_user_info call.

  This call includes the options for full details of credentials
  and credential attributes.
  """
  return {
      'requestId': '7229df6c_4b86_4aa3_bfe4_7f07fe6c52c4',
      'status': '0000',
      'statusMessage': 'Success',
      'detail': None,
      'detailMessage': None,
      'userId': 'karl@example.com',
      'userCreationTime': datetime.datetime(2017, 8, 15, 1, 15, 14, 555000, tzinfo=pytz.UTC),
      'userStatus': 'LOCKED',
      'numBindings': 1,
      'credentialBindingDetail': [
          {
              'credentialId': 'SYMC21519954',
              'credentialType': 'STANDARD_OTP',
              'credentialStatus': 'ENABLED',
              'tokenCategoryDetails': {
                  'CategoryId': 70,
                  'FormFactor': 'MOBILE',
                  'MovingFactor': 'TIME',
                  'OtpGeneratedBy': 'SOFTWARE'
              },
              'tokenInfo': {
                  'TokenId': {
                      '_value_1': 'SYMC21519954',
                      'type': None
                  },
                  'TokenKind': 'SOFTWARE',
                  'Adapter': 'OATH_TIME',
                  'TokenStatus': 'ENABLED',
                  'ExpirationDate': datetime.datetime(2038, 1, 1, 0, 0, 0, 205000, tzinfo=pytz.UTC),
                  'TempPasswordExpirationDate': None,
                  'TempPasswordOneTimeUse': None,
                  'LastUpdate': datetime.datetime(2017, 11, 9, 2, 13, tzinfo=pytz.UTC),
                  'ServerOTPExpires': None,
                  'TokenGroupId': None,
                  'Owner': False,
                  'ReportedReason': None
              },
              'bindingDetail': {
                  'bindStatus': 'ENABLED',
                  'friendlyName': 'nexus',
                  'trustedDevice': None,
                  'clientVersion': None,
                  'clientType': None,
                  'lastBindTime': datetime.datetime(2017, 8, 17, 2, 37, 51, 909000, tzinfo=pytz.UTC),
                  'lastAuthnTime': datetime.datetime(2017, 11, 9, 2, 13, 0, 22000, tzinfo=pytz.UTC),
                  'lastAuthnId': '7CE4BB604887BEAD'
              },
              'pushAttributes': [
                  {
                      'Key': 'BIO_FINGERPRINT_CAPABLE',
                      'Value': 'false'
                  },
                  {
                      'Key': 'PUSH_PLATFORM',
                      'Value': 'ANDROID'
                  },
                  {
                      'Key': 'PUSH_ENABLED',
                      'Value': 'true'
                  },
                  {
                      'Key': 'BIO_FINGERPRINT_ENABLED',
                      'Value': 'false'
                  },
                  {
                      'Key': 'FIRST_FACTOR_CAPABLE',
                      'Value': 'true'
                  }
              ]
          }
      ],
      'isPinSet': None,
      'isTempPasswordSet': None,
      'pinExpirationTime': None
      }

@pytest.fixture
def get_user_info_multiple_credentials_xml():
  """XML response from API.

  This data is the XML version of that stored in the equivalently named _json
  fixture.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><GetUserInfoResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>be2f95be_515f_49e9_b842_2eb2eb4db371</requestId><status>0000</status><statusMessage>Success</statusMessage><userId>karl@example.com</userId><userCreationTime>2017-08-15T01:15:14.555Z</userCreationTime><userStatus>ACTIVE</userStatus><numBindings>3</numBindings><credentialBindingDetail><credentialId>SYDC23459775</credentialId><credentialType>STANDARD_OTP</credentialType><credentialStatus>ENABLED</credentialStatus><tokenCategoryDetails><CategoryId>72</CategoryId><FormFactor>DESKTOP</FormFactor><MovingFactor>TIME</MovingFactor><OtpGeneratedBy>SOFTWARE</OtpGeneratedBy></tokenCategoryDetails><tokenInfo><TokenId>SYDC23459775</TokenId><TokenKind>SOFTWARE</TokenKind><Adapter>OATH_TIME</Adapter><TokenStatus>ENABLED</TokenStatus><ExpirationDate>2038-01-01T00:00:00.259Z</ExpirationDate><LastUpdate>2018-01-06T02:51:00.000Z</LastUpdate><Owner>false</Owner></tokenInfo><bindingDetail><bindStatus>ENABLED</bindStatus><friendlyName>VIP Access for Mac v2 (current)</friendlyName><lastBindTime>2018-01-05T04:48:43.256Z</lastBindTime><lastAuthnTime>2018-01-06T02:51:00.224Z</lastAuthnTime><lastAuthnId>AAD1693BDA5E4C09</lastAuthnId></bindingDetail></credentialBindingDetail><credentialBindingDetail><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType><credentialStatus>ENABLED</credentialStatus><tokenCategoryDetails><CategoryId>70</CategoryId><FormFactor>MOBILE</FormFactor><MovingFactor>TIME</MovingFactor><OtpGeneratedBy>SOFTWARE</OtpGeneratedBy></tokenCategoryDetails><tokenInfo><TokenId>SYMC21519954</TokenId><TokenKind>SOFTWARE</TokenKind><Adapter>OATH_TIME</Adapter><TokenStatus>ENABLED</TokenStatus><ExpirationDate>2038-01-01T00:00:00.291Z</ExpirationDate><LastUpdate>2018-01-05T00:10:06.000Z</LastUpdate><Owner>false</Owner></tokenInfo><bindingDetail><bindStatus>ENABLED</bindStatus><friendlyName>nexus</friendlyName><lastBindTime>2017-08-17T02:37:51.909Z</lastBindTime><lastAuthnTime>2018-01-05T00:10:06.371Z</lastAuthnTime><lastAuthnId>3B706CAD59BE44FE</lastAuthnId></bindingDetail><pushAttributes><Key>BIO_FINGERPRINT_CAPABLE</Key><Value>false</Value></pushAttributes><pushAttributes><Key>PUSH_PLATFORM</Key><Value>ANDROID</Value></pushAttributes><pushAttributes><Key>PUSH_ENABLED</Key><Value>true</Value></pushAttributes><pushAttributes><Key>BIO_FINGERPRINT_ENABLED</Key><Value>false</Value></pushAttributes><pushAttributes><Key>FIRST_FACTOR_CAPABLE</Key><Value>true</Value></pushAttributes></credentialBindingDetail><credentialBindingDetail><credentialId>VSST43994978</credentialId><credentialType>STANDARD_OTP</credentialType><credentialStatus>ENABLED</credentialStatus><tokenCategoryDetails><CategoryId>72</CategoryId><FormFactor>DESKTOP</FormFactor><MovingFactor>TIME</MovingFactor><OtpGeneratedBy>SOFTWARE</OtpGeneratedBy></tokenCategoryDetails><tokenInfo><TokenId>VSST43994978</TokenId><TokenKind>SOFTWARE</TokenKind><Adapter>OATH_TIME</Adapter><TokenStatus>ENABLED</TokenStatus><ExpirationDate>2038-01-01T00:00:00.319Z</ExpirationDate><LastUpdate>2018-01-05T04:34:15.000Z</LastUpdate><Owner>false</Owner></tokenInfo><bindingDetail><bindStatus>ENABLED</bindStatus><friendlyName>VIP Access for Mac</friendlyName><lastBindTime>2018-01-05T04:34:15.190Z</lastBindTime></bindingDetail></credentialBindingDetail></GetUserInfoResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def get_user_info_credentials_multiple_credentials_json():
  """Return full API output from a user's get_user_info call.

  This call includes the options for full details of credentials
  and credential attributes and includes THREE bindings (one push capable, two
  not). This means the function name is now a bit of a misnomer.
  """
  return {
    'requestId': 'be2f95be_515f_49e9_b842_2eb2eb4db371',
    'status': '0000',
    'statusMessage': 'Success',
    'detail': None,
    'detailMessage': None,
    'userId': 'karl@example.com',
    'userCreationTime': datetime.datetime(2017, 8, 15, 1, 15, 14, 555000, tzinfo=pytz.UTC),
    'userStatus': 'ACTIVE',
    'numBindings': 3,
    'credentialBindingDetail': [
        {
            'credentialId': 'SYDC23459775',
            'credentialType': 'STANDARD_OTP',
            'credentialStatus': 'ENABLED',
            'tokenCategoryDetails': {
                'CategoryId': 72,
                'FormFactor': 'DESKTOP',
                'MovingFactor': 'TIME',
                'OtpGeneratedBy': 'SOFTWARE'
            },
            'tokenInfo': {
                'TokenId': {
                    '_value_1': 'SYDC23459775',
                    'type': None
                },
                'TokenKind': 'SOFTWARE',
                'Adapter': 'OATH_TIME',
                'TokenStatus': 'ENABLED',
                'ExpirationDate': datetime.datetime(2038, 1, 1, 0, 0, 0, 259000, tzinfo=pytz.UTC),
                'TempPasswordExpirationDate': None,
                'TempPasswordOneTimeUse': None,
                'LastUpdate': datetime.datetime(2018, 1, 6, 2, 51, tzinfo=pytz.UTC),
                'ServerOTPExpires': None,
                'TokenGroupId': None,
                'Owner': False,
                'ReportedReason': None
            },
            'bindingDetail': {
                'bindStatus': 'ENABLED',
                'friendlyName': 'VIP Access for Mac v2 (current)',
                'trustedDevice': None,
                'clientVersion': None,
                'clientType': None,
                'lastBindTime': datetime.datetime(2018, 1, 5, 4, 48, 43, 256000, tzinfo=pytz.UTC),
                'lastAuthnTime': datetime.datetime(2018, 1, 6, 2, 51, 0, 224000, tzinfo=pytz.UTC),
                'lastAuthnId': 'AAD1693BDA5E4C09'
            },
            'pushAttributes': []
        },
        {
            'credentialId': 'SYMC21519954',
            'credentialType': 'STANDARD_OTP',
            'credentialStatus': 'ENABLED',
            'tokenCategoryDetails': {
                'CategoryId': 70,
                'FormFactor': 'MOBILE',
                'MovingFactor': 'TIME',
                'OtpGeneratedBy': 'SOFTWARE'
            },
            'tokenInfo': {
                'TokenId': {
                    '_value_1': 'SYMC21519954',
                    'type': None
                },
                'TokenKind': 'SOFTWARE',
                'Adapter': 'OATH_TIME',
                'TokenStatus': 'ENABLED',
                'ExpirationDate': datetime.datetime(2038, 1, 1, 0, 0, 0, 291000, tzinfo=pytz.UTC),
                'TempPasswordExpirationDate': None,
                'TempPasswordOneTimeUse': None,
                'LastUpdate': datetime.datetime(2018, 1, 5, 0, 10, 6, tzinfo=pytz.UTC),
                'ServerOTPExpires': None,
                'TokenGroupId': None,
                'Owner': False,
                'ReportedReason': None
            },
            'bindingDetail': {
                'bindStatus': 'ENABLED',
                'friendlyName': 'nexus',
                'trustedDevice': None,
                'clientVersion': None,
                'clientType': None,
                'lastBindTime': datetime.datetime(2017, 8, 17, 2, 37, 51, 909000, tzinfo=pytz.UTC),
                'lastAuthnTime': datetime.datetime(2018, 1, 5, 0, 10, 6, 371000, tzinfo=pytz.UTC),
                'lastAuthnId': '3B706CAD59BE44FE'
            },
            'pushAttributes': [
                {
                    'Key': 'BIO_FINGERPRINT_CAPABLE',
                    'Value': 'false'
                },
                {
                    'Key': 'PUSH_PLATFORM',
                    'Value': 'ANDROID'
                },
                {
                    'Key': 'PUSH_ENABLED',
                    'Value': 'true'
                },
                {
                    'Key': 'BIO_FINGERPRINT_ENABLED',
                    'Value': 'false'
                },
                {
                    'Key': 'FIRST_FACTOR_CAPABLE',
                    'Value': 'true'
                }
            ]
        },
        {
            'credentialId': 'VSST43994978',
            'credentialType': 'STANDARD_OTP',
            'credentialStatus': 'ENABLED',
            'tokenCategoryDetails': {
                'CategoryId': 72,
                'FormFactor': 'DESKTOP',
                'MovingFactor': 'TIME',
                'OtpGeneratedBy': 'SOFTWARE'
            },
            'tokenInfo': {
                'TokenId': {
                    '_value_1': 'VSST43994978',
                    'type': None
                },
                'TokenKind': 'SOFTWARE',
                'Adapter': 'OATH_TIME',
                'TokenStatus': 'ENABLED',
                'ExpirationDate': datetime.datetime(2038, 1, 1, 0, 0, 0, 319000, tzinfo=pytz.UTC),
                'TempPasswordExpirationDate': None,
                'TempPasswordOneTimeUse': None,
                'LastUpdate': datetime.datetime(2018, 1, 5, 4, 34, 15, tzinfo=pytz.UTC),
                'ServerOTPExpires': None,
                'TokenGroupId': None,
                'Owner': False,
                'ReportedReason': None
            },
            'bindingDetail': {
                'bindStatus': 'ENABLED',
                'friendlyName': 'VIP Access for Mac',
                'trustedDevice': None,
                'clientVersion': None,
                'clientType': None,
                'lastBindTime': datetime.datetime(2018, 1, 5, 4, 34, 15, 190000, tzinfo=pytz.UTC),
                'lastAuthnTime': None,
                'lastAuthnId': None
            },
            'pushAttributes': []
        }
    ],
    'isPinSet': None,
    'isTempPasswordSet': None,
    'pinExpirationTime': None
}



@pytest.fixture
def get_user_info_no_credentials_xml():
  """Return API output from get_user_info as XML.

  This is the data returned from the API before being processed by Zeep.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><GetUserInfoResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>7ffb63d5_aa78_4755_acd3_4600d78dab4f</requestId><status>0000</status><statusMessage>Success</statusMessage><userId>karl+testing@example.com</userId><userCreationTime>2017-09-26T04:58:12.416Z</userCreationTime><userStatus>ACTIVE</userStatus><numBindings>0</numBindings></GetUserInfoResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def get_user_info_no_credentials_json():
  """Return API output from get_user_info with a non existent user as XML.

  This returns a user with no credentials.
  """
  return {
      'requestId': '7ffb63d5_aa78_4755_acd3_4600d78dab4f',
      'status': '0000',
      'statusMessage': 'Success',
      'detail': None,'detailMessage': None,
      'userId': 'karl+testing@example.com',
      'userCreationTime': datetime.datetime(2017, 9, 26, 4, 58, 12, 416000, tzinfo=pytz.UTC),
      'userStatus': 'ACTIVE',
      'numBindings': 0,
      'credentialBindingDetail': [],
      'isPinSet': None,
      'isTempPasswordSet': None,
      'pinExpirationTime': None
      }

@pytest.fixture
def get_user_info_user_does_not_exist_xml():
  """Return API output from get_user_info as XML.

  This is the data returned from the API before being processed by Zeep.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><GetUserInfoResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>6f09c809_9bcf_4507_899e_057e4c9d0eeb</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></GetUserInfoResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def get_user_info_user_does_not_exist_json():
  """Return API output from get_user_info with a non existent user as XML.

  This is the data returned from the API after being processed by Zeep.
  """
  return {
    'requestId': '6f09c809_9bcf_4507_899e_057e4c9d0eeb',
    'status': '6003',
    'statusMessage': 'User does not exist.',
    'detail': None,
    'detailMessage': None,
    'userId': None,
    'userCreationTime': None,
    'userStatus': None,
    'numBindings': None,
    'credentialBindingDetail': [],
    'isPinSet': None,
    'isTempPasswordSet': None,
    'pinExpirationTime': None
    }

def validate_token_data_successful_validation():
  """Return from successful validation of a token code."""
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>acd96095_6e14_49a6_b338_1e877b2bc128</requestId><status>0000</status><statusMessage>Success</statusMessage><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType><authnId>C3908206F2DCABCF</authnId></AuthenticateUserResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def validate_token_data_user_unknown_to_vip_xml():
  """XML returned for a query involving an unknown user.

  The json component is not required for testing as the test doesn't require
  it.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>07a803d4_587a_4847_9211_38b14781debf</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></AuthenticateUserResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def validate_token_data_token_has_letter_xml():
  """Response from API when token code includes letter.

  No json component required for the test.
  """
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>a3c53830_7a31_421c_ae2b_5d1133ffe3b9</requestId><status>6009</status><statusMessage>Authentication failed.</statusMessage></AuthenticateUserResponse></S:Body></S:Envelope>"""
  return xml


@pytest.fixture
def validate_token_data_user_is_locked_xml():
  """Response from API when user account is locked.

  No json component required for the test.
  """
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>1920851e_d94e_4dc6_87f9_541b0b38e6ad</requestId><status>601B</status><statusMessage>Operation not allowed in current user status.</statusMessage></AuthenticateUserResponse></S:Body></S:Envelope>"""
  return xml

@pytest.fixture
def validate_token_data_code_too_long_xml():
  """Response from API when code is too long.

  This appears to be any time the API doesn't expect the code that was sent

  No json component required for the test.
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>26349f7d_6502_459d_928d_cab4b9ae4eb7</requestId><status>6009</status><statusMessage>Authentication failed.</statusMessage><detail>49B5</detail><detailMessage>Failed with an invalid OTP</detailMessage></AuthenticateUserResponse></S:Body></S:Envelope>"""
  return xml

# WIP

def api_update_user_unlocking_user_xml():
  """Response from API when unlocking user.

  Idimpotent - running on active account gives identical output
  """
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>4e1f1b62_9623_482b_b6e1_234005edf51b</requestId><status>0000</status><statusMessage>Success</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
  return xml

def api_update_user_user_does_not_exist_xml():
  """Response from API when unlocking user that does not exist.

  Idimpotent - running on active account gives identical output
  """
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><UpdateUserResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>537b12c0_35f6_4e3b_b69c_e0700cf0a3f0</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></UpdateUserResponse></S:Body></S:Envelope>"""
  return xml

def utils_send_user_auth_push_request_sent_xml():
  """Successfully trigger a mobile push request.

  This means your post to the VIP API was successful and generated a push
  notification for the user.
  """
  # Not sure why this attempt was not utf8 encoded but the lower attempt is. Keeping around in case it turns out to be useful for some sort of weird bug .
  # xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>d56c9859_65e7_471d_abc3_c293494454ef</requestId><status>6040</status><statusMessage>Mobile push request sent</statusMessage><transactionId>4f8110763104a278</transactionId><pushDetail><pushCredentialId>SYMC21519954</pushCredentialId><pushSent>true</pushSent></pushDetail></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>00c6066b_61d3_4b51_ad1d_34709e5b1af9</requestId><status>6040</status><statusMessage>Mobile push request sent</statusMessage><transactionId>2ae68a940ec4236b</transactionId><pushDetail><pushCredentialId>SYMC21519954</pushCredentialId><pushSent>true</pushSent></pushDetail></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml


def utils_send_user_auth_push_invalid_user_xml():
  """Response if we attempt to trigger a push to an unkonwn user."""
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>713aefbb_668d_4bff_a0d9_8d3823292116</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml

def utils_send_user_auth_push_user_has_no_credentials():
  """Response if we try and trigger a push to a user with no compatible credential."""
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>92d62705_a622_44cb_be4c_0d7ed57d529f</requestId><status>6008</status><statusMessage>User does not have any enabled credential for the given credential type.</statusMessage></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml



def utils_poll_user_auth_push_in_progress_xml():
  """Wait for user to acknowledge the push response.

  Polling API to determine if the user has approved or denied the push request
  - user has not yet actioned our push.
  """
  # Not yet accepted push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>1111b918_7d5f_4409_8bc4_b3db2d873445</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>2ae68a940ec4236b</transactionId><status>7001</status><statusMessage>Mobile push request in progress</statusMessage></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_user_approved_xml():
  """User has approved our request.

  The API informs us that the user has approved our push request
  """
# Successful/accepted push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>3cc3429d_32be_4f37_8a49_b43a9b955ab5</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>2ae68a940ec4236b</transactionId><status>7000</status><statusMessage>Mobile push request approved by user</statusMessage><authnTime>1970-01-01T00:00:00.000Z</authnTime><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_user_denied_xml():
  """User has denied our request.

  The API informs us that the user has denied our push request.
  """
  # denied push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>769c659e_e305_4467_ac6e_4db274d8c362</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>0bd24cf0c94caefa</transactionId><status>7002</status><statusMessage>Mobile push request denied by user</statusMessage><authnTime>1970-01-01T00:00:00.000Z</authnTime><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_unknown_request_id():
  """Response to any unknown/unexpected transaction ID.

  As long as the request ID is valid (>=4 characters) there isno difference
  between "invalid" and "unknown" for the API.
  """
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>cfdbb016_af01_4180_81fd_b63ccaf3b428</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>23456</transactionId><status>7005</status><statusMessage>Mobile push request not found</statusMessage></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_send_user_auth_push_request_sent_xml():
  """Successfully trigger a mobile push request.

  This means your post to the VIP API was successful and generated a push
  notification for the user.
  """
  # Not sure why this attempt was not utf8 encoded but the lower attempt is. Keeping around in case it turns out to be useful for some sort of weird bug .
  # xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>d56c9859_65e7_471d_abc3_c293494454ef</requestId><status>6040</status><statusMessage>Mobile push request sent</statusMessage><transactionId>4f8110763104a278</transactionId><pushDetail><pushCredentialId>SYMC21519954</pushCredentialId><pushSent>true</pushSent></pushDetail></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>00c6066b_61d3_4b51_ad1d_34709e5b1af9</requestId><status>6040</status><statusMessage>Mobile push request sent</statusMessage><transactionId>2ae68a940ec4236b</transactionId><pushDetail><pushCredentialId>SYMC21519954</pushCredentialId><pushSent>true</pushSent></pushDetail></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml


def utils_send_user_auth_push_invalid_user_xml():
  """Response if we attempt to trigger a push to an unkonwn user."""
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>713aefbb_668d_4bff_a0d9_8d3823292116</requestId><status>6003</status><statusMessage>User does not exist.</statusMessage></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml

def utils_send_user_auth_push_user_has_no_credentials():
  """Response if we try and trigger a push to a user with no compatible credential."""
  xml = """<?xml version="1.0" ?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><AuthenticateUserWithPushResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>92d62705_a622_44cb_be4c_0d7ed57d529f</requestId><status>6008</status><statusMessage>User does not have any enabled credential for the given credential type.</statusMessage></AuthenticateUserWithPushResponse></S:Body></S:Envelope>"""
  return xml



def utils_poll_user_auth_push_in_progress_xml():
  """Wait for user to acknowledge the push response.

  Polling API to determine if the user has approved or denied the push request
  - user has not yet actioned our push.
  """
  # Not yet accepted push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>1111b918_7d5f_4409_8bc4_b3db2d873445</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>2ae68a940ec4236b</transactionId><status>7001</status><statusMessage>Mobile push request in progress</statusMessage></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_user_approved_xml():
  """User has approved our request.

  The API informs us that the user has approved our push request
  """
# Successful/accepted push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>3cc3429d_32be_4f37_8a49_b43a9b955ab5</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>2ae68a940ec4236b</transactionId><status>7000</status><statusMessage>Mobile push request approved by user</statusMessage><authnTime>1970-01-01T00:00:00.000Z</authnTime><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_user_denied_xml():
  """User has denied our request.

  The API informs us that the user has denied our push request.
  """
  # denied push (poll_push_notification)
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>769c659e_e305_4467_ac6e_4db274d8c362</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>0bd24cf0c94caefa</transactionId><status>7002</status><statusMessage>Mobile push request denied by user</statusMessage><authnTime>1970-01-01T00:00:00.000Z</authnTime><credentialId>SYMC21519954</credentialId><credentialType>STANDARD_OTP</credentialType></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml

def utils_poll_user_auth_push_unknown_request_id():
  """Response to any unknown/unexpected transaction ID.

  As long as the request ID is valid (>=4 characters) there isno difference
  between "invalid" and "unknown" for the API.
  """
  xml = """<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><PollPushStatusResponse xmlns="https://schemas.symantec.com/vip/2011/04/vipuserservices"><requestId>cfdbb016_af01_4180_81fd_b63ccaf3b428</requestId><status>0000</status><statusMessage>Success</statusMessage><transactionStatus><transactionId>23456</transactionId><status>7005</status><statusMessage>Mobile push request not found</statusMessage></transactionStatus></PollPushStatusResponse></S:Body></S:Envelope>"""
  return xml


