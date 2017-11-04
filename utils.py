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

def send_user_auth_push(user):
  """Facilitate authenticating with a push notification to a device via
  Symantec VIP
  Takes a user object
  """
  logger.debug('Initialising SendUserAuthPush with user {0}'.format(user))
  email = user.email

  logger.debug('Attempting to send push requst')
  auth_authenticate_user_with_push = authenticate_user_with_push(email)
  # print auth_authenticate_user_with_push
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
  """Using a transactionId returned by SendUserAuthPush, wait to determine if
  the user authenticates successfully.
  This returns True on success and False on authentication or error conditions
  Takes a string containing the transaction ID generated in SendUserAuthPush
  """

  logger.debug('Initialising PollUserAuthPush')

  # Sleep before running the query, user needs time to respond (Assumes this is
  # run immediately after SendUserAuthPush)
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


def validate_token_data():
  """Facilitate authenticating with a token supplied code.
  Takes a user object and string for the code
  """
  logger.debug('Initialising ValidateTokenData with user {0} and code {1}'.format(user, token))
  if user.email:
    email = user.email
  else:
    logger.info('{0} has no email address'.format(user))
    return False

  logger.debug('Attempting to send push request for user {0} with data {1}'.format( email, token))
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
  pass

def add_device():
  pass

