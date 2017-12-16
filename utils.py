"""Utility functions.

Most of these are wrappers around the API, but some are helpers created for
other purposes.
"""

# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# For now()
import datetime

# For sleep()
import time

from django_otp_vip import api

from django.contrib.auth.models import User

from .models import VipUser, VipBaseCredential
from .credential_models import VipPushCredential

# TODO: Raise ValidationError for our errors instead of just logging them


# NOTE: several functions that should be here were moved to models because screw you circular imports :(



def create_remote_vip_user(email):
  """Create record for user in VIP."""
  return api.create_user(email)

def disable_remote_vip_user(email):
  """Disable record for user in VIP."""
  return api.update_user(email, new_user_status='DISABLED')

# TODO: combine these two methods
def query_user_info(user):
  """Query APi for user details.
  
  Does not include full information wrt credentials.
  """
  return get_user_info(user)

def query_user_credential_details(user):
  """Extensive information about the credentials."""
  user_details = api.get_user_info(user, includePushAttributes=True, includeTokenInfo=True)
  if user_details.status == '0000':
    # a list
    return user_details['credentialBindingDetail']
  if user_details.status == 6003:
    # user does not exist
    return []

def add_credential_to_vip():
  """Add new credential to users VIP account.

  TODO: add call to add_credential_to_user()
  """
  pass

def update_user_credentials(supplied_data):
  """Update credential records in DB.
  
  Take a list of credentials (as returned by query_user_credential_details) or
  the full user details and update each of them in the db.
  Returns true or false to indicate success or failure.
  """
  logger.debug('in update_user_credentials')
  logger.debug(supplied_data)
  if 'userId' in supplied_data:
    logger.debug('Full user details supplied, splitting out required information')
    user_credentials = supplied_data['credentialBindingDetail']
    user = discover_user_from_email(supplied_data['userId'])
  else:
    # FIXME: Assumes everything is ok
    logger.debug('No userId found, assuming we were passed user credentials')
    user_credentials = supplied_data

  if not user_credentials:
    logger.debug('No credentials to update')
    return True

  if not user:
    logger.debug('Unable to create or update credential without user object')
    return False

  logger.debug('looping %s credentials' % len(user_credentials))
  for current_credential in user_credentials:

    for attrib in current_credential['pushAttributes']:
      if attrib['Key'] == 'PUSH_PLATFORM':
        # TODO: is this available on non push compatible credentials? there but empty? if yes move this code
        push_platform = attrib['Value']
      if (attrib['Key'] == 'PUSH_ENABLED') and (attrib['Value'] == 'true'):
        push_enabled_credential = True

    logger.debug('Working with credential %s' % current_credential['credentialId'])
    try:
      record = VipBaseCredential.objects.get(credential_id=current_credential['credentialId'] )
      logger.debug('Active record is %s, based on credential %s' % (record, current_credential['credentialId']))
    except VipBaseCredential.DoesNotExist:
      logger.debug('No record found for credential %s' % current_credential['credentialId'])

      if push_enabled_credential:
        logger.debug('Creating with VipPushCredential type')
        record = VipPushCredential()
        record.push_enabled = True
        record.attribute_platform = push_platform
      else:
        # FIXME: this may need added complexity later, like more elif checks for different credentials
        logger.debug('Creating with VipBaseCredential type')
        record = VipBaseCredential()

    logger.debug('About to update credential %s' % current_credential['credentialId'])
    record.user = user
    record.credential_id = current_credential['credentialId']
    record.credential_type = current_credential['credentialType']
    record.credential_status = current_credential['credentialStatus']
    record.token_form_factor = current_credential['tokenCategoryDetails']['FormFactor']
    record.token_kind = current_credential['tokenInfo']['TokenKind']
    record.token_adaptor = current_credential['tokenInfo']['Adapter']
    record.token_status = current_credential['tokenInfo']['TokenStatus']
    record.token_expiration_date = current_credential['tokenInfo']['ExpirationDate']
    record.token_last_update = current_credential['tokenInfo']['LastUpdate']
    # FIXME: silently failed to record on first run. bug?
    record.friendly_name = current_credential['bindingDetail']['friendlyName']
    record.bind_status = current_credential['bindingDetail']['bindStatus']
    record.bind_time = current_credential['bindingDetail']['lastBindTime']
    record.last_authn_time = current_credential['bindingDetail']['lastAuthnTime']
    # Same as transaction_id?
    record.last_authn_id = current_credential['bindingDetail']['lastAuthnId']

    record.save()
    return True

def update_user_record(info_from_api):
  """Update VIP user data stored in DB.
  
  Accepts a dict, as returned by query_user_info
  Returns True or False to indicate success or failure.
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
  except AttributeError as ae:
    logger.debug('Unable to map %s to a user: can\'t update record' % info_from_api['userId'])
    return False
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
  """Establish the local user from email address.
  
  TODO: Consider removing from this app.
  TODO: share this in oh so many parts of our codebase
  Pass in an email address and a user object will be returned.
  None if no user found
  """
  if not email:
    logger.debug('discover_user_from_email requires an email be passed')
    return None

  user_list = User.objects.filter(email=email)
  if not user_list:
    print 'No local user with email %s, unable to continue' % email
    return None
  if len(user_list) > 1:
    logger.debug('Warning, %s has multiple accounts in local system (%s), returning first' % (email, user_list))

  return user_list[0]

def update_vip_user_records(user):
  """Update both user and credential DB records."""
  full_user_details = get_user_info(user.email, includePushAttributes=True, includeTokenInfo=True)
  if not full_user_details.status == '0000':
    print('user does not exist, logging of error will occur later')
    return False

  try:
    # Update the users "personal information"
    update_user_record(full_user_details)

    # Update all credential records in DB
    update_user_credentials(full_user_details)
    return True
  except Exception as ee:
    print 'adfadfa'
    print ee
    return False

