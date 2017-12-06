# These live here because the circular import with utils triggered breakage
# when I created the VipUser class. Python, wtf.

import logging
logger = logging.getLogger(__name__)

from django.db import models

# from .utils import send_user_auth_push, poll_user_auth_push, validate_token_data

from models import VipBaseDevice



from .api import authenticate_user_with_push, poll_push_status, authenticate_user

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


class VipPushDevice(VipBaseDevice):
  """Records devices capable of receiving Symantec VIP push authentication
  requests"""
  last_updated = models.DateTimeField(auto_now=True, verbose_name='Updated at')
  latest_transaction_id = models.CharField(max_length=30, editable=False)
  attribute_platform = models.CharField(max_length=30, editable=False)

  def generate_challenge(self):
    """Send request for a push to Symantec VIP servers
    This method runs self.save() to record the transaction id.
    """
    logger.debug('Calling send_user_auth_push and recording its transaction ID')
    auth_attempt = send_user_auth_push(self.user)
    if auth_attempt is not None:
      logger.debug('Auth attempt dictionary: %s' % auth_attempt.__dict__)
      self.latest_transaction_id = auth_attempt.transaction_id
      self.save(update_fields=['latest_transaction_id'])
      return str('Sent (Check your device).')
    else:
      return str('An error occurred trying to send the push')

  def verify_token(self, *args):
    """Poll Symantec VIP service for a response to the push request"""
    if args:
      logger.debug('Unexpected arguments: {0}, skipping validation against this device'.format(args))
      return False
    # Do we have a transaction ID to query?
    if not self.latest_transaction_id:
      return False
    # poll_user_auth_push will run for the time configured in
    # VIP_POLL_SLEEP_SECONDS times VIP_POLL_SLEEP_MAX_COUNT
    logger.debug('Running poll_user_auth_push with transaction ID %s' % self.latest_transaction_id)
    # This returns True or False depending on the result
    return poll_user_auth_push(self.latest_transaction_id)


# FIXME: consider renaming this so we can use yubikey/recover codes/freeotp as
# TokenDevice. Depends on how these models interact with the supplied models (remmeber this is just for vip)
class VipTokenDevice(VipBaseDevice):
  """Records VIP compatible devices which generate authentication codes"""
  token_code = models.CharField(max_length=30, default='')

  def verify_token(self, token):
    """Check with Symantec VIP service if this token should be considered
    valid"""
    self.token_code = token
    self.save()
    logger.debug("Calling validate_token_data with user {0} and token {1}".format(self.user, token))
    return validate_token_data(self.user, token)


# FIXME: Do these two have existing classes i can override?
# - possibly via twillio, django-otp-twilio 
# TODO: This will have to wait until I have a chance to set up SMS on VIP
# class SmsDevice(VipBaseDevice):
#   """Records devices which can receive SMS' via VIP"""
#   # FIXME: needs to check if user has specified phone number. Bail if they haven't.
# if phone nubmer in user profile, use it, else number passed as param to init, use it. else fail
#   pass

# class CallDevice(VipBaseDevice):
#   """Records devices which can receive a call via VIP"""
#   # FIXME: needs to check if user has specified phone number. Bail if they haven't.
# if phone nubmer in user profile, use it, else number passed as param to init, use it. else fail
#   pass


