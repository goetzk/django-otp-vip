# https://docs.djangoproject.com/en/1.8/topics/settings/#using-settings-in-python-code

import os

try:
  VIP_CERT_LOCATION
  print('Using pre set VIP_CERT_LOCATION')
except NameError:
  print('Setting VIP_CERT_LOCATION')
  VIP_CERT_LOCATION = os.path.dirname(__file__) + '/certs/'

try:
  VIP_WSDL_LOCATION
  print('Using pre set VIP_WSDL_LOCATION')
except NameError:
  print('Setting VIP_WSDL_LOCATION')
  VIP_WSDL_LOCATION = os.path.dirname(__file__) + '/wsdls/'

VIP_CERTIFICATE_PUBLIC  = VIP_CERT_LOCATION + 'user_services_public.crt'
VIP_CERTIFICATE_PRIVATE = VIP_CERT_LOCATION + 'user_services_decrypted.key'
VIP_WSDL_USERSERVICES_QUERY = VIP_WSDL_LOCATION + 'vipuserservices-query-1.8.wsdl'
VIP_WSDL_USERSERVICES_AUTH  = VIP_WSDL_LOCATION + 'vipuserservices-auth-1.8.wsdl'
VIP_WSDL_USERSERVICES_MGMT  = VIP_WSDL_LOCATION + 'vipuserservices-mgmt-1.8.wsdl'
VIP_POLL_SLEEP_SECONDS = 10
VIP_POLL_SLEEP_MAX_COUNT = 10

