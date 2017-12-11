"""API calls to Symantec.

All API calls are collated in to this module.
"""
# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# To determine project path
import os

# For now()
import datetime

# For sleep()
import time

# For request IDs
import uuid

# soap library
import zeep

# Needed to suppress InsecureRequestWarning
import urllib3

# Modifying the session
import requests

# Suppress InsecureRequestWarning from urllib3
# The InsecureRequestWarning from urllib3 says to look at
# https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl-py2
# Ignore that and look at https://stackoverflow.com/a/28002687
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Restructure in the spirit of https://github.com/bennylope/pydiscourse/blob/master/pydiscourse/client.py
class VIPClient():
  """Symantec VIP SOAP API endpoint client"""

  def __init__(self,
                custom_session = None,
                custom_transport = None,
                public_cert  = os.path.dirname(__file__) + '/certs/' + 'user_services_public.crt',
                private_cert = os.path.dirname(__file__) + '/certs/' + 'user_services_decrypted.key',
                auth_wsdl  =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-query-1.8.wsdl',
                mgmt_wsdl  =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-auth-1.8.wsdl',
                query_wsdl =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-mgmt-1.8.wsdl',
                *args, **kwargs):
    """Initialise API client(s!)

    Args:
      custom_session: requests.Session() object. This REPLACES the class internal session so you are required to do all session setup.
      custom_transport: zeep.transports.Transport() object. This REPLACES the class internal transport so you are required to do all transport setup.
      public_cert Public half of the SSL certificate used to authenticate with Symantec VIP
      private_cert: Private half of the SSL certificate used to authenticate with Symantec VIP
      auth_wsdl: Location of Authentication API endpoints WSDL file in a zeep.Client() compatible location
      mgmt_wsdl: Location of Management API endpoints WSDL file in a zeep.Client() compatible location
      query_wsdl: Location of Query API endpoints WSDL file in a zeep.Client() compatible location
      *args, **kwargs)
    """

    self.session = custom_session
    self.transport = custom_transport
    self.certificate_public_half = public_cert
    self.certificate_private_half = private_cert
    self.auth_wsdl = auth_wsdl
    self.mgmt_wsdl = mgmt_wsdl
    self.query_wsdl = query_wsdl

    if not self.session:
      # Will use requests to set certificate
      # http://docs.python-requests.org/en/latest/user/advanced/#client-side-certificates
      # TODO: try/except this
      logger.debug('Setting up custom Requests Session()')
      self.session = requests.Session()

      # "SSLError(SSLError(1, u'[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure" and similar mean: add certificates
      logger.debug('Importing certificates')
      self.session.cert = (self.certificate_public_half, self.certificate_private_half)

    if not self.transport:
      # http://docs.python-zeep.org/en/master/transport.html?highlight=requests#ssl-verification
      logger.debug('Creating custom Zeep transport')
      self.transport = zeep.transports.Transport(session=self.session)

    # Create client instances
    logger.debug('Creating API clients')
    auth_client = zeep.Client( wsdl=self.auth_wsdl, transport=self.transport)
    mgmt_client =  zeep.Client( wsdl=self.mgmt_wsdl, transport=self.transport)
    query_client = zeep.Client( wsdl=self.query_wsdl, transport=self.transport)

def make_request_id():
  """Produce a unique ID for each request."""
  return str(uuid.uuid4()).replace('-', '_')

def authenticate_user_with_push(user_id, push_auth_data={}):
  """Trigger a push authentication request via Symantec."""
  return auth_client.service.authenticateUserWithPush(requestId=make_request_id(), userId = user_id, pushAuthData = push_auth_data)

def poll_push_status(transaction_ids = [] ):
  """Check to see if a pushed authentication request has been actioned."""
  return query_client.service.pollPushStatus(requestId=make_request_id(), transactionId = transaction_ids)

def authenticate_user(user_id, otp_auth_data={}):
  """Validate token code entered by user."""
  return auth_client.service.authenticateUser(requestId=make_request_id(), userId = user_id, otpAuthData = otp_auth_data)

def get_user_info(user_id, **kwargs):
  """Query for user details.

  This can be run in two ways:
  - Without arguments (includes information like name, identifier, status
    (locked or not) and creation time)
  - With includePushAttributes=True and or includeTokenInfo=True (Add if a
    credential can support push authentication and detailed credential
    information respectively).
  """
  return query_client.service.getUserInfo(requestId=make_request_id(), userId = user_id, **kwargs )


def create_user(user_id):
  """Create a new user in VIP."""
  return mgmt_client.service.createUser(requestId=make_request_id(), userId = user_id)


def update_user(user_id, new_user_status=None, new_user_id=None):
  """
  Update user ID or Enable/Disable user.

  newUserId is required if user is changing email address
  newUserStatus is optional, value can be ACTIVE or DISABLED. This is how users are disabled/re-enabled!
  NOTE: as written, can only do one of status/id update per run
  """
  # If the user has a new status, change them.
  if new_user_status:
    return mgmt_client.service.updateUser(requestId=make_request_id(), userId = user_id, newUserStatus=new_user_status)
  if new_user_id:
    return mgmt_client.service.updateUser(requestId=make_request_id(), userId = user_id, newUserId=new_user_id)


def add_credential_to_user(user_id, credential_id, credential_type = 'STANDARD_OTP', friendly_name = None):
  """Add a new credential to an existing user."""
  # This one is a bit more complicated! 
  return mgmt_client.service.addCredential(requestId=make_request_id(), userId = user_id,
                        credentialDetail = { 
                            'credentialId' : credential_id.replace(' ', ''),
                            'credentialType' : credential_type,
                            'friendlyName' : friendly_name
                            })

