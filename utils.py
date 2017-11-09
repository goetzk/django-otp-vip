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

from models import VipUser

# TODO: Raise ValidationError for our errors instead of just logging them

def send_user_auth_push(user, token={}):
  """Facilitate authenticating with a push notification to a device via
  Symantec VIP
  Takes a user object
  """
  email = user.email
  logger.debug('Initialising send_user_auth_push with user {0}, email {1}'.format(user, email))

  logger.debug('Attempting to send push request for user {0} with data {1}'.format( email, token))
  auth_authenticate_user_with_push = authenticate_user_with_push(email, token)
  logger.debug('Checking request return code')
  if auth_authenticate_user_with_push.status == '6040':
    push_transaction_id = auth_authenticate_user_with_push.transactionId
    push_sent = datetime.datetime.now()
    logger.debug('Authentication push %s sent at %s' % (push_transaction_id, push_sent))
  else:
    # Something other than a successful send
    push_transaction_id = None
    logger.debug( "Problem when trying to send push. Error ID %s: %s" % (auth_authenticate_user_with_push.status, auth_authenticate_user_with_push.statusMessage))
  return push_transaction_id


def poll_user_auth_push(transaction):
  """Using a transactionId returned by send_user_auth_push, wait to determine if
  the user authenticates successfully.
  This returns True on success and False on authentication or error conditions
  Takes a string containing the transaction ID generated in send_user_auth_push
  """

  logger.debug('Initialising poll_user_auth_push')

  # Sleep before running the query, user needs time to respond (Assumes this is
  # run immediately after send_user_auth_push)
  logger.debug('Sleeping for %s seconds' % VIP_POLL_SLEEP_SECONDS)
  time.sleep(VIP_POLL_SLEEP_SECONDS)

  still_waiting = True
  num_sleeps = 0

  logger.debug('About to start wait loop')
  while still_waiting:
    try:
      logger.debug('Polling to check status of request')
      query_poll_push_status = poll_push_status([transaction])
    except zeep.exceptions.ValidationError as zevee:
      logger.debug("Data Validation error: %s" % zevee)
      return False

    if not len(query_poll_push_status.transactionStatus):
      logger.debug('Somehow we\'ve arrived here with no transactions to poll. Returning false')
      still_waiting = False
      return False

    # Should only be one item in this list
    logger.debug('Checking %s transactionStatus items' % len(query_poll_push_status.transactionStatus))
    for push in query_poll_push_status.transactionStatus:
      logger.debug( 'Transaction %s is status %s: %s' % (push.transactionId, push.status, push.statusMessage))
      if push.status == '7000':
        logger.debug("Transaction %s approved at %s" % (push.transactionId, datetime.datetime.now()))
        still_waiting = False
        return True
      if push.status == '7001':
        # If we've been waiting for 10 iterations of our sleep its time to give up.
        if num_sleeps == VIP_POLL_SLEEP_MAX_COUNT:
          logger.debug("Transaction %s is taking too long, giving up up after %s sleeps of %s seconds" % (push.transactionId, num_sleeps, VIP_POLL_SLEEP_SECONDS))
          still_waiting = False
          return False
        logger.debug('Still waiting for %s' % push.transactionId)
        time.sleep(VIP_POLL_SLEEP_SECONDS)
        num_sleeps += 1
      else:
        # Auth failed
        logger.debug( "Authentication of transaction %s has failed. Message returned was %s (code %s)" % (push.transactionId, push.statusMessage, push.status))
        still_waiting = False
        return False


def validate_token_data(user, token):
  """Facilitate authenticating with a token supplied code.
  Takes a user object and string for the code
  """
  logger.debug('Initialising ValidateTokenData with user {0} and code {1}'.format(user, token))
  if user.email:
    email = user.email
  else:
    logger.info('{0} has no email address'.format(user))
    return False

  auth_authenticate_user = authenticate_user( email, token)
  logger.debug('Checking request return code')
  if auth_authenticate_user.status == '0000':
    logger.debug('Authentication succeeded at %s' % datetime.datetime.now())
    return True
  else:
    # Something other than a successful send
    logger.debug( "Problem with authentication. Error ID {0}: {1}(Detail code {2}, {3})".format(auth_authenticate_user.status, auth_authenticate_user.statusMessage, auth_authenticate_user.detail, auth_authenticate_user.detailMessage))
    return False




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

