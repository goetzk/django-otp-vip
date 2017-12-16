"""Utility functions.

Most of these are wrappers around the API, but some are helpers created for
other purposes.
"""

# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# For now()
import datetime

# To add timezone data to dates
import pytz

# For sleep()
import time

from django_otp_vip import api

from django.contrib.auth.models import User

from .models import VipUser
from .credential_models import VipPushCredential, VipTokenCredential

# TODO: Raise ValidationError for our errors instead of just logging them


# NOTE: several functions that should be here were moved to models because screw you circular imports :(



def create_remote_vip_user(email):
  """Create record for user in VIP."""
  result = api.create_user(email)
  return result

def disable_remote_vip_user(email):
  """Disable record for user in VIP."""
  result = api.update_user(user_id = email, new_user_status='DISABLED')
  return result

def query_user_info(user):
  """Query APi for user details.

  This function expects a string it can use with the VIP API.

  Includes extensive information about associated credentials, supplied as a list.
  """
  if type(user) not in [ str, unicode ]:
    logger.debug('query_user_info requires a string be passed in')
    return False

  logger.debug('query_user_info requesting information for {0}'.format(user))
  user_details = api.get_user_info(user, includePushAttributes=True, includeTokenInfo=True)
  # logger.debug('query_user_info has gathered the following data for this user. {0}'.format(user_details))
  if user_details.status == '0000':
    logger.debug('Query was successful')
    # a dictionary
    return user_details
  if user_details.status == '6003':
    logger.debug('Query was not successful')
    # user does not exist, empty dict
    return {}

def add_credential_to_vip(email, credential, name):
  """Add new credential to users VIP account.

  TODO: add call to add_credential_to_user()
  """
  result = api.add_credential_to_user(user_id = email, credential_id = credential, friendly_name=name)
  return result

def update_user_credentials(supplied_data):
  """Update credential records in DB.

  Takes full user details from query_user_info and updates User + credential records in DB.
  Returns true or false to indicate success or failure.
  """
  logger.debug('in update_user_credentials')
  if supplied_data:
    logger.debug('Full user details supplied, splitting out required information')
    try:
      user_credentials = supplied_data['credentialBindingDetail']
      user = discover_user_from_email(supplied_data['userId'])
    except TypeError as te:
      logger.debug('Was passed invalid data ({0})'.format(supplied_data))
      return False
  else:
    logger.debug('Nothing supplied:')
    logger.debug(supplied_data)
    return False

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
        logger.debug('Push platform is %s' % push_platform)

      if (attrib['Key'] == 'PUSH_ENABLED') and (attrib['Value'] == 'true'):
        logger.debug('Push enabled value is %s' % attrib['Value'])
        push_enabled_credential = True
      elif (attrib['Key'] == 'PUSH_ENABLED') and (attrib['Value'] == 'false'):
        logger.debug('Push enabled value is %s' % attrib['Value'])
        push_enabled_credential = False

    logger.debug('Working with credential %s' % current_credential['credentialId'])

    try:
      if push_enabled_credential:
        record = VipPushCredential.objects.get(credential_id=current_credential['credentialId'] )
      else:
        record = VipTokenCredential.objects.get(credential_id=current_credential['credentialId'] )
      # If/else has no finally and for some reason this debug message isn't being done
      logger.debug('Active record is %s, based on credential %s' % (record, current_credential['credentialId']))
    except VipBaseCredential.DoesNotExist:
      logger.debug('No record found for credential %s' % current_credential['credentialId'])

      if push_enabled_credential:
        logger.debug('Creating with VipPushCredential type')
        record = VipPushCredential()
        record.push_enabled = True
        record.attribute_platform = push_platform
      else: # FIXME: this may need added complexity later, like more elif checks for different credentials
        logger.debug('Creating with VipTokenCredential type')
        record = VipTokenCredential()
        record.push_enabled = False

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
    logger.debug('Record saved')
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
  # FIXME: VipUser is not imported, and i suspect that is due to (you guessed it) loops.
  except VipUser.DoesNotExist as rodne:
    # We have a user, but they don't have a VipUser record.
    logger.debug('No existing VipUser object for %s, creating one now' % info_from_api['userId'])
    user_details = VipUser()
  except AttributeError as ae:
    # A NoneType object was returned by discover_user_from_email - no user mapped
    logger.debug('Unable to map %s to a user: can\'t update record' % info_from_api['userId'])
    return False

  time_for_db = info_from_api['userCreationTime']
  # Make time object timezone aware if it isn't already
  if time_for_db.tzinfo is None or time_for_db.tzinfo.utcoffset(time_for_db) is None:
    logger.debug('Date supplied for vip_created_at is not timezone aware. Attempting to add UTC timezone')
    time_for_db = time_for_db.replace(tzinfo=pytz.utc)

  logger.debug("Updating VipUser instance for %s" % info_from_api['userId'])
  user_details.user = current_user
  user_details.vip_user_id = info_from_api['userId']
  # I'm 90% sure all times (except server time) are UTC
  user_details.vip_created_at = time_for_db
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
    logger.debug('No local user with email %s, unable to continue' % email)
    return None
  if len(user_list) > 1:
    logger.debug('Warning, %s has multiple accounts in local system (%s), returning first' % (email, user_list))

  return user_list[0]

def update_vip_user_records(info_from_api):
  """Update both user and credential DB records.

  This accepts output from query_user_info()
  """
  # Update the users "personal information"
  user_result = update_user_record(info_from_api)

  # Update all credential records in DB
  credential_result = update_user_credentials(info_from_api)

  if user_result and credential_result:
    return True

  return False

