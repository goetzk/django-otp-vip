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

# For error handling
import zeep

from otp_vip import api

from django.contrib.auth.models import User

from .models import VipUser

VIP_POLL_SLEEP_SECONDS = 10
VIP_POLL_SLEEP_MAX_COUNT = 10


def create_remote_vip_user(email):
  """Create record for user in VIP."""
  result = api.create_user(email)
  return result

def disable_remote_vip_user(email):
  """Disable record for user in VIP."""
  result = api.update_user(user_id = email, new_user_status='DISABLED')
  return result

def rename_remote_vip_user(email, newemail):
  """Disable record for user in VIP."""
  result = api.update_user(user_id = email, new_user_id = newemail)
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
  """Add new credential to users VIP account."""
  result = api.add_credential_to_user(user_id = email, credential_id = credential, friendly_name=name)
  return result

def remove_credential_from_vip(email, credential):
  """Remove a credential from users VIP account.

  Users can only have a limited number of credentials registered, and sometimes
  an upgrade can replace the credential id!
  """
  result = api.remove_credential_from_user(user_id = email, credential_id = credential)
  return result


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
  except KeyError as ke:
    logger.debug('Couldn\'t determine user from API data. ({0})'.format(info_from_api))
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

def send_user_auth_push(email, token={}):
  """Facilitate authenticating with a push notification.

  Takes a user object and triggers an authentication request to a credential
  via Symantec VIP
  """
  if not email:
    logger.debug('No user supplied')
    return None

  logger.debug('Attempting to send push request for user {0} with optional data {1}'.format(email, token))
  auth_authenticate_user_with_push = api.authenticate_user_with_push(email, token)
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
  """Poll Symantec VIP service to see if push notification has been actioned.

  Using a transactionId returned by send_user_auth_push, wait to determine if
  the user authenticates successfully.
  This returns True on success and False on authentication or error conditions
  Takes a string containing the transaction ID generated in send_user_auth_push
  """
  logger.debug('Initialising poll_user_auth_push')

  if not transaction:
    logger.debug('No transaction id provided')
    return False

  still_waiting = True
  num_sleeps = 0

  logger.debug('About to start wait loop')
  while still_waiting:
    try:
      logger.debug('Polling to check status of request')
      query_poll_push_status = api.poll_push_status([transaction])
    except zeep.exceptions.ValidationError as zevee:
      logger.debug("Data Validation error: %s" % zevee)
      still_waiting = False
      return False
    except zeep.exceptions.XMLSyntaxError as xse:
      logger.debug("Data retrieved from API was invalid. {0}".format(xse))
      still_waiting = False
      return False

    # Should only be one item in this list
    logger.debug('Checking %s transactionStatus items' % len(query_poll_push_status.transactionStatus))
    for push in query_poll_push_status.transactionStatus:
      logger.debug( 'Transaction %s is status %s: %s' % (push.transactionId, push.status, push.statusMessage))
      if push.status == '7000':
        logger.debug("Transaction %s approved at %s" % (push.transactionId, datetime.datetime.now()))
        still_waiting = False
        result = True
      elif push.status == '7001':
        # If we've been waiting for 10 iterations of our sleep its time to give up.
        if num_sleeps == VIP_POLL_SLEEP_MAX_COUNT:
          logger.debug("Transaction %s is taking too long, giving up up after %s sleeps of %s seconds" % (push.transactionId, num_sleeps, VIP_POLL_SLEEP_SECONDS))
          still_waiting = False
          result = False
        logger.debug('Still waiting for %s' % push.transactionId)
        time.sleep(VIP_POLL_SLEEP_SECONDS)
        num_sleeps += 1
      else:
        # Auth failed
        logger.debug( "Authentication of transaction %s has failed. Message returned was %s (code %s)" % (push.transactionId, push.statusMessage, push.status))
        still_waiting = False
        result = False

  logger.debug('About to return result of push validation for {0}: {1}'.format(push.transactionId, result))
  # At the end of the loop return the result
  return result

def validate_token_data(email, token):
  """Facilitate authenticating with a token supplied code.

  Takes an email and string for the code
  """
  logger.debug('Initialising ValidateTokenData with user {0} and code {1}'.format(email, token))
  if not email:
    logger.info('No email address supplied (given ({0})'.format(email))
    return False

  auth_authenticate_user = api.authenticate_user( email, token)
  logger.debug('Checking request return code')
  if auth_authenticate_user.status == '0000':
    logger.debug('Authentication succeeded at %s' % datetime.datetime.now())
    return True
  else:
    # Something other than a successful send
    logger.debug( "Problem with authentication. Error ID {0}: {1}(Detail code {2}, {3})".format(auth_authenticate_user.status, auth_authenticate_user.statusMessage, auth_authenticate_user.detail, auth_authenticate_user.detailMessage))
    return False

