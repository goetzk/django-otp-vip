"""Classes required to create and configuge the API clients.

The only class defined here that should be needed elsewhere is VIPClient.
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

# soap library
import zeep

# Needed to suppress InsecureRequestWarning
import urllib3

# Modifying the session
import requests

# Required for XML manipulation (which I haven't got working yet anyway...)
from lxml import etree

# Suppress InsecureRequestWarning from urllib3
# The InsecureRequestWarning from urllib3 says to look at
# https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl-py2
# Ignore that and look at https://stackoverflow.com/a/28002687
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PluginVipCustomisation(zeep.Plugin):
  """Plugin to hook in to Zeeps' send/receive API data processing.

  Two methods re provided here to check the validity of VIP calls,
  _check_status_code and _check_detail_code. They are run by the egress method
  to perform extra checks against the XML we receive from Symantec so we can
  raise errors early, and from one location.

  I am hoping to have egress modify the XML being sent so it automatically
  includes the requestId and we can stop including it in every API call.
  Problem is, Zeep validates the calls and won't allow this to be done without
  adding an override to every call - thereby generating as much work as it
  saves.

  BOTH PLUGINS ARE CURRENTLY NO-OPS
  """

  def egress(self, envelope, http_headers, operation, binding_options):
    """Add requestId to all API calls (BROKEN).

    # This would be possible but zeep does validation which occurs before plugins are run - see
    # http://docs.python-zeep.org/en/master/datastructures.html#skipvalue
    # At the moment it requires an xsd skip added to every query - no improvement on adding the random value there.
    # from django_otp_vip.api import VIPClient, IngressOutput; i = IngressOutput(); c = VIPClient(plugins=[i]) ;
    # query_client = c.query_client ; query_client.service.getUserInfo(userId = 'karl@kgoetz.id.au', requestId=xsd.SkipValue)

    """
#     print('in egress')
#     envelope = etree.tostring(envelope).replace('<ns0:requestId/>', '<ns0:requestId>{0}</ns0:requestId>'.format(rand()))
    return envelope, http_headers

  def ingress(self, envelope, http_headers, operation):
    """Perform API return validity checking."""
    # print('in ingress')
    # print type(envelope)
    # print(etree.tostring(envelope, pretty_print=True))
    # Check status code
    self._check_status_code(envelope)
    self._check_detail_code(envelope)
    return envelope, http_headers

  def _check_status_code(self, supplied_data):
    """Determine if the API call was successful from its status code.

    Checks the API status and messages values to establish if the Symantec API
    considers this query successful.
    These values were taken from VIP_UserServices.pdf, Appending A (pages 125 -
    130)

    """
    return True

  def _check_detail_code(self, supplied_data):
    """Check extra details of API return.

    Optional extra information to help diagnose queries.

    These values were taken from VIP_UserServices.pdf, Appending A (pages 131 -
    133)

    """
    return True


class ConfigureClients(object):
  """Symantec VIP SOAP API endpoint client.

  This is a thin wrapper around the Zeep SOAP client, it exists only to
  perform setup and provide a few helper methods for validating returned
  queries.
  """

  def __init__(self,
                custom_session = None,
                custom_transport = None,
                public_cert  = os.path.dirname(__file__) + '/certs/' + 'user_services_public.crt',
                private_cert = os.path.dirname(__file__) + '/certs/' + 'user_services_decrypted.key',
                auth_wsdl  =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-auth-1.8.wsdl',
                mgmt_wsdl  =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-mgmt-1.8.wsdl',
                query_wsdl =   os.path.dirname(__file__) + '/wsdls/' + 'vipuserservices-query-1.8.wsdl',
                plugins = [],
                *args, **kwargs
                ):
    """Initialise API client(s!).

    Args:
      custom_session: requests.Session() object. This REPLACES the class internal session so you are required to do all session setup.
      custom_transport: zeep.transports.Transport() object. This REPLACES the class internal transport so you are required to do all transport setup.
      public_cert Public half of the SSL certificate used to authenticate with Symantec VIP
      private_cert: Private half of the SSL certificate used to authenticate with Symantec VIP
      auth_wsdl: Location of Authentication API endpoints WSDL file in a zeep.Client() compatible location
      mgmt_wsdl: Location of Management API endpoints WSDL file in a zeep.Client() compatible location
      query_wsdl: Location of Query API endpoints WSDL file in a zeep.Client() compatible location
      plugins: List of Zeep.plugin.Plugin() objects. This REPLACES the class internal plugin setup
      *args, **kwargs)
    """
    self.certificate_public_half = public_cert
    self.certificate_private_half = private_cert
    self.auth_wsdl = auth_wsdl
    self.mgmt_wsdl = mgmt_wsdl
    self.query_wsdl = query_wsdl

    if custom_session:
      self.session = custom_session
    else:
      # Will use requests to set certificate
      # http://docs.python-requests.org/en/latest/user/advanced/#client-side-certificates
      logger.debug('Setting up custom Requests Session()')
      self.session = requests.Session()

      # "SSLError(SSLError(1, u'[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure" and similar mean: add certificates
      logger.debug('Importing certificates')
      self.session.cert = (self.certificate_public_half, self.certificate_private_half)

    if custom_transport:
      self.transport = custom_transport
    else:
      # http://docs.python-zeep.org/en/master/transport.html?highlight=requests#ssl-verification
      logger.debug('Creating custom Zeep transport')
      self.transport = zeep.transports.Transport(session=self.session)

    if plugins:
      self.plugins = plugins
    else:
      self.plugins = [PluginVipCustomisation()]

    logger.debug('Creating API clients using WSDLs, transport and plugins')
    self.auth_client  = zeep.Client( wsdl=self.auth_wsdl, transport=self.transport, plugins=self.plugins)
    self.mgmt_client  = zeep.Client( wsdl=self.mgmt_wsdl, transport=self.transport, plugins=self.plugins)
    self.query_client = zeep.Client( wsdl=self.query_wsdl, transport=self.transport, plugins=self.plugins)

