# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# Import configuration
from .settings import VIP_POLL_SLEEP_SECONDS, VIP_POLL_SLEEP_MAX_COUNT

# For now()
import datetime

# For sleep()
import time

from .api import *
# TODO: move to this
# import .api

from django.contrib.auth.models import User

from .models import VipUser, VipBaseDevice
from .device_models import VipPushDevice

# TODO: Raise ValidationError for our errors instead of just logging them


# NOTE: several functions that should be here were moved to models because screw you circular imports :(



def create_remote_vip_user(email):
  """Create record for user in VIP."""
  create_user(email)

def disable_remote_vip_user(email):
  """Disable record for user in VIP."""
  update_user(email, new_user_status='DISABLED')

# TODO: combine these two methods
def query_user_info(user):
  """ Does not include full information wrt devices"""
  user_details = get_user_info(user)

def query_user_device_details(user):
  """extensive information about the devices, probably more than is needed"""
  user_details = get_user_info(user, includePushAttributes=True, includeTokenInfo=True)
  if user_details.status == '0000':
    # a list
    return user_details['credentialBindingDetail']
  if user_details.status == 6003:
    # user does not exist
    return []

def add_device_to_vip():
  pass

def update_user_devices(supplied_data):
  """Take a list of devices (as returned by query_user_device_details) or the
  full user details and update each of them in the db.
  Returns true or false to indicate success or failure"""

  logger.debug('in update_user_devices')
  logger.debug(supplied_data)
  if 'userId' in supplied_data:
    logger.debug('Full user details supplied, splitting out required information')
    user_credentials = supplied_data['credentialBindingDetail']
    user = discover_user_from_email(supplied_data['userId'])
  else:
    # Assume everuthign is ok
    user_devices = supplied_data

  if not user_devices:
    logger.debug('No devices to update')
    return True

  logger.debug('looping %s devices' % len(user_devices))
  for current_device in user_devices:

    for attrib in current_device['pushAttributes']:
      if attrib['Key'] == 'PUSH_PLATFORM':
        # TODO: is this available on non push compatible devices? there but empty? if yes move this code
        push_platform = attrib['Value']
      if (attrib['Key'] == 'PUSH_ENABLED') and (attrib['Value'] == 'true'):
        push_enabled_device = True

    logger.debug('Working with credential %s' % current_credential['credentialId'])

    # FIXME: VipBaseCredential can no longer be accessed directly. convert to VipPushCredential and VipTokenCredential.
    try:
      record = VipBaseCredential.objects.get(credential_id=current_credential['credentialId'] )
      logger.debug('Active record is %s, based on credential %s' % (record, current_credential['credentialId']))
    except Exception as ee:
      logger.debug('No record found for credential %s' % current_credential['credentialId'])
      if not user:
        logger.debug('Unable to create new credential without user object')
        return False

      if push_enabled_device:
        logger.debug('Creating with VipPushDevice type')
        record = VipPushDevice()
        record.push_enabled = True
        record.attribute_platform = push_platform
      else:
        # FIXME: this may need added complexity later, like more elif checks for different devices
        logger.debug('Creating with VipBaseDevice type')
        record = VipBaseDevice()

    logger.debug('About to update credential %s' % current_device['credentialId'])
    record.user = user
    record.credential_id = current_device['credentialId']
    record.credential_type = current_device['credentialType']
    record.credential_status = current_device['credentialStatus']
    record.token_form_factor = current_device['tokenCategoryDetails']['FormFactor']
    record.token_kind = current_device['tokenInfo']['TokenKind']
    record.token_adaptor = current_device['tokenInfo']['Adapter']
    record.token_status = current_device['tokenInfo']['TokenStatus']
    record.token_expiration_date = current_device['tokenInfo']['ExpirationDate']
    record.token_last_update = current_device['tokenInfo']['LastUpdate']
    # FIXME: silently failed to record on first run. bug?
    record.friendly_name = current_device['bindingDetail']['friendlyName']
    record.bind_status = current_device['bindingDetail']['bindStatus']
    record.bind_time = current_device['bindingDetail']['lastBindTime']
    record.last_authn_time = current_device['bindingDetail']['lastAuthnTime']
    # Same as transaction_id?
    record.last_authn_id = current_device['bindingDetail']['lastAuthnId']

    record.save()
    return True

def update_user_record(info_from_api):
  """accepts a dict, as returned by query_user_info
  Returns True or False to indicate success or failure
  """
  # Locate record
  try:
    current_user = discover_user_from_email(info_from_api['userId'])
  except KeyError as ke:
    logger.debug('Couldn\'t determine user from API data. ({0})'.format(info_from_api))
    return False
  except TypeError as te:
    logger.debug('update_user_record received invalid data, expecting a dictionary, received {0}'.format(info_from_api))
    return False

  try:
    user_details = current_user.vipuser
  except VipUser.DoesNotExist as rodne:
    logger.debug('No existing VipUser object for %s, creating one now' % info_from_api['userId'])
    user_details = VipUser()

  print("Updating VipUser instance for %s" % info_from_api['userId'])
  user_details.user = current_user
  user_details.vip_user_id = info_from_api['userId']
  user_details.vip_created_at = info_from_api['userCreationTime']
  user_details.status = info_from_api['userStatus']
  user_details.bindings_count = info_from_api['numBindings']
  user_details.pin_set = info_from_api['isPinSet']
  user_details.pin_expiration_time = info_from_api['pinExpirationTime']
  user_details.temp_password_set = info_from_api['isTempPasswordSet']
  user_details.save()
  return True

def discover_user_from_email(email):
  """TODO: share this in oh so many parts of our codebase
  Pass in an email address and a user object will be returned.
  None if no user found
  """
  user_list = User.objects.filter(email=email)
  if not user_list:
    print 'No local user with email %s, unable to continue' % email
    return None
  if len(user_list) > 1:
    print 'Warning, %s has multiple accounts in local system (%s), returning first' % (email, user_list)

  return user_list[0]

def update_vip_user_records(user):
  full_user_details = get_user_info(user.email, includePushAttributes=True, includeTokenInfo=True)
  if not full_user_details.status == '0000':
    print('user does not exist, logging of error will occur later')
    pass

  try:
    # Update the users "personal information"
    update_user_record(full_user_details)

    # Update all credential records in DB
    update_user_credentials(full_user_details)
  except Exception as ee:
    print 'adfadfa'
    print ee

