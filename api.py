# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# Import configuration
from .settings import VIP_CERTIFICATE_PUBLIC, VIP_CERTIFICATE_PRIVATE
from .settings import VIP_WSDL_USERSERVICES_QUERY, VIP_WSDL_USERSERVICES_AUTH, VIP_WSDL_USERSERVICES_MGMT

# Suppress InsecureRequestWarning from urllib3
# The InsecureRequestWarning from urllib3 says to look at
# https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl-py2
# Ignore that and look at https://stackoverflow.com/a/28002687
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# For now()
import datetime

# For sleep()
import time

# For request IDs
import uuid

# soap library
import zeep


# Use requests to set certificate
# http://docs.python-requests.org/en/latest/user/advanced/#client-side-certificates
from requests import Session
logger.debug('Setting up custom Requests Session()')
session = Session()
# "SSLError(SSLError(1, u'[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure" and similar mean: add certificates
logger.debug('Importing certificates')
session.cert = (VIP_CERTIFICATE_PUBLIC, VIP_CERTIFICATE_PRIVATE)

# http://docs.python-zeep.org/en/master/transport.html?highlight=requests#ssl-verification
from zeep.transports import Transport
logger.debug('Creating custom Zeep transport')
transport = Transport(session=session)


# Specify wsdl to use when making client, there are 3 possibilities depending on the task at hand:

# Create client instances
logger.debug('Creating api clients')
query_client = zeep.Client( wsdl=VIP_WSDL_USERSERVICES_QUERY, transport=transport)
auth_client = zeep.Client( wsdl=VIP_WSDL_USERSERVICES_AUTH, transport=transport)
mgmt_client =  zeep.Client( wsdl=VIP_WSDL_USERSERVICES_MGMT, transport=transport)


def make_request_id():
  """Utility function to produce a unique ID for each request"""
  return str(uuid.uuid4()).replace('-', '_')

def authenticate_user_with_push(user_id, push_auth_data={}):
  
  return auth_client.service.authenticateUserWithPush(requestId=make_request_id(), userId = user_id, pushAuthData = push_auth_data)

def poll_push_status(transaction_ids = [] ):
  return query_client.service.pollPushStatus(requestId=make_request_id(), transactionId = transaction_ids)

def authenticate_user(user_id, otp_auth_data={}):
  return auth_client.service.authenticateUser(requestId=make_request_id(), userId = user_id, otpAuthData = otp_auth_data)

def get_user_info(user_id, **kwargs):

  return query_client.service.getUserInfo(requestId=make_request_id(), userId = user_id, **kwargs )


def create_user(user_id):
  return mgmt_client.service.createUser(requestId=make_request_id(), userId = user_id)


def update_user(user_id, new_user_status='ACTIVE', new_user_id=None):
# updateUser (including disable access)

# newUserId is required if user is changing email address
# newUserStatus is optional, value can be ACTIVE or DISABLED. This is how users are disabled/re-enabled!
  return mgmt_client.service.updateUser(requestId=make_request_id(), userId = user_id, newUserStatus=new_user_status)


def add_device_to_user(user_id, credential_id, credential_type = 'STANDARD_OTP', friendly_name = None):
# This one is a bit more complicated! 
  return mgmt_client.service.addCredential(requestId=make_request_id(), userId = user_id,
                        credentialDetail = { 
                            'credentialId' : credential_id.replace(' ', ''),
                            'credentialType' : credential_type,
                            'friendlyName' : friendly_name
                            })

