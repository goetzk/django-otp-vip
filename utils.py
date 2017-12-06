# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

# Import configuration
from .settings import VIP_POLL_SLEEP_SECONDS, VIP_POLL_SLEEP_MAX_COUNT

# For now()
import datetime

# For sleep()
import time

from api import authenticate_user_with_push, poll_push_status, authenticate_user
from api import get_user_info

from django.contrib.auth.models import User

from .models import VipUser, VipBaseDevice
from .device_models import VipPushDevice

# TODO: Raise ValidationError for our errors instead of just logging them


# NOTE: several functions that should be here were moved to models because screw you circular imports :(



def create_user():
  pass

def disable_user():
  # update_user(to a disabled sate)
  pass

def query_user_info(user):
  # Does not include full information wrt devices
  user_details = get_user_info(user)

def query_user_device_details(user):
  # extensive information about the devices, probably more than is needed
  user_details = get_user_info(user, includePushAttributes=True, includeTokenInfo=True)
  if user_details.status == '0000':
    # a list
    return user_details['credentialBindingDetail']
  if user_details.status == 6003:
    # user does not exist
    return []

def add_device():
  pass

def update_user_devices(user_devices):
  # Take a list of devices (as returned by query_user_device_details) and
  # update each of them in the db


  for d in user_devices:
    try:
      record = VipBaesDevice.objects.get(credential_id=current_device['credentialId'] )
    except NotFound:
      record = VipBaesDevice()

    record.credential_id = current_device['credentialId']
    record.credential_type = current_device['credentialType']
    record.credential_status = current_device['credentialStatus']
    record.token_form_factor = current_device['tokenCategoryDetails']['FormFactor']
    record.token_kind = current_device['tokenInfo']['TokenKind']
    record.token_adaptor = current_device['tokenInfo']['OATH_TIME']
    record.token_status = current_devicee['tokenInfo']['TokenStatus']
    record.token_expiration_date = current_devicee['tokenInfo']['ExpirationDate']
    record.token_last_update = current_devicee['tokenInfo']['LastUpdate']
    record.friendly_name = current_device['bindingDetail']['friendlyName']
    record.bind_status = current_device['bindingDetail']['bindStatus']
    record.bind_time = current_device['bindingDetail']['lastBindTime']
    record.last_authn_time = current_device['bindingDetail']['lastAuthnTime']
    # Same as transaction_id?
    record.last_authn_id = current_device['bindingDetail']['lastAuthnId']

    # FIXME: If object is a push token, also need to update these
    # FIXME: is this available on non push compatible devices? there but empty?
    if current_device['pushAttributes']['PUSH_PLATFORM']:
	    record.attribute_platform = current_device['pushAttributes']['PUSH_PLATFORM']

    if current_device['pushAttributes']['PUSH_ENABLED']:
      record.push_enabled = True

    record.save()

def update_user_record(info_from_api):
  # accepts a dict, as returned by query_user_info
  # Locate record
  try:
    user_list = User.objects.filter(email=info_from_api['userId'])
  except Exception as ee:
    print 'no user with email %s, unable to continue' % info_from_api['userId']
    # FIXME: pass is wrong here
    pass
  if len(user_list) > 1:
    print 'warning, user has multiple accounts in local system (%s)' % user

  try:
    user_details = user_list[0].vipuserdetails
  except VipUser.RelatedObjectDoesNotExist as rodne:
    user_details = VipUser()
  
  user_details.user = user_list[0]
  user_details.vip_user_id = info_from_api['userId']
  user_details.vip_created_at = info_from_api['userCreationTime']
  user_details.status = info_from_api['userStatus']
  user_details.bindings_count = info_from_api['numBindings']
  user_details.pin_set = info_from_api['isPinSet']
  user_details.pin_expiration_time = info_from_api['pinExpirationTime']
  user_details.temp_password_set = info_from_api['isTempPasswordSet']
  user_details.save()

def update_vip_user_records(user):
  full_user_details = get_user_info(user.email, includePushAttributes=True, includeTokenInfo=True)
  if not full_user_details.status == '0000':
    pass
    # user does not exist
    # log error etc

  # Update the users "personal information"
  update_user_record(full_user_details)

  # Update all credential records in DB
  update_user_devices(full_user_details['credentialBindingDetail'])

