"""Test instantiation class for API clients.

Our API client creator (and supporting plugin) has a lot of moving parts so can
reasonably do with some testing of its own.

The plugin will need substantial testing once it is complete, it has several
helper methods.

"""
from otp_vip.api_configuration import PluginVipCustomisation, ConfigureClients

import requests
import zeep

# Testing current behaviour of all Plugin methods, these will need to change when it starts to /do something/

def test_check_status_code_returns_true():
  """_check_status_code method is currently hard coded to return true."""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance._check_status_code('replace me with real xml') == True

def test_check_detail_code_returns_true():
  """_check_status_code method is currently hard coded to return true."""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance._check_detail_code('replace me with real xml') == True


def test_egress_returns_envelope_unchanged():
  """At the moment all supplied arguments are passed through untouched"""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance.egress('envelope', 'http_headers', 'operation', 'binding_options') == ('envelope', 'http_headers')

def test_egress_returns_headers_unchanged():
  """At the moment all supplied arguments are passed through untouched"""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance.egress('envelope', 'http_headers', 'operation', 'binding_options') == ('envelope', 'http_headers')

def test_ingress_returns_envelope_unchanged():
  """At the moment all supplied arguments are passed through untouched"""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance.ingress('envelope', 'http_headers', 'operation') == ('envelope', 'http_headers')

def test_ingress_returns_headers_unchanged():
  """At the moment all supplied arguments are passed through untouched"""
  plugin_instance = PluginVipCustomisation()
  assert plugin_instance.ingress('envelope', 'http_headers', 'operation') == ('envelope', 'http_headers')


# And client setup

def test_auth_client_instantiated():
  """Simple test to ensure the auth client has been created. This test does not check the clients function"""
  client = ConfigureClients()
  assert client.auth_client

def test_mgmt_client_instantiated():
  """Simple test to ensure the mgmt client has been created. This test does not check the clients function"""
  client = ConfigureClients()
  assert client.mgmt_client

def test_query_client_instantiated():
  """Simple test to ensure the query client has been created. This test does not check the clients function"""
  client = ConfigureClients()
  assert client.query_client

def test_client_custom_plugin():
  """Ensure session is set to the value in custom_session if it is passed in"""
  client = ConfigureClients(plugins=[PluginVipCustomisation])
  assert client.plugins == [PluginVipCustomisation]

def test_client_custom_session():
  """Ensure session is set to the value in custom_session if it is passed in"""
  c_session = requests.Session()
  client = ConfigureClients(custom_session=c_session)
  assert client.session == c_session

def test_client_custom_transport():
  """Ensure transport is set to the value of custom_transport if it is passed in"""
  c_session = requests.Session()
  c_transport = zeep.transports.Transport(session=c_session)
  client = ConfigureClients(custom_transport = c_transport)
  assert client.transport == c_transport

def test_client_custom_transport_ignores_custom_session():
  """Ensure a custom transports session is not replaced if we supply a custom session"""
  i_session = requests.Session()
  c_session = requests.Session()
  c_transport = zeep.transports.Transport(session=c_session)
  client = ConfigureClients(custom_session = i_session, custom_transport = c_transport)
  assert client.transport.session == c_session

