"""
Credential related Models and helper methods they depend on.

To mitigate against circular import issues and to keep 'base classes' separate
from these Credential related classes these live in their own file rather than
models.py
"""
import logging
logger = logging.getLogger(__name__)

from django.db import models

import time

from .models import VipBaseCredential
from otp_vip import utils

def save_modified_record(record, user_obj, credential_json):
  """Update and save credential DB entries.

  Should be passed an object derived from VipBaseCredential.
  """
  logger.debug('About to update credential %s' % credential_json['credentialId'])
  record.user = user_obj
  record.credential_id = credential_json['credentialId']
  record.credential_type = credential_json['credentialType']
  record.credential_status = credential_json['credentialStatus']
  record.token_form_factor = credential_json['tokenCategoryDetails']['FormFactor']
  record.token_kind = credential_json['tokenInfo']['TokenKind']
  record.token_adaptor = credential_json['tokenInfo']['Adapter']
  record.token_status = credential_json['tokenInfo']['TokenStatus']
  record.token_expiration_date = credential_json['tokenInfo']['ExpirationDate']
  record.token_last_update = credential_json['tokenInfo']['LastUpdate']
  record.name = '{0} (Push enabled {1})'.format(credential_json['bindingDetail']['friendlyName'], record.push_enabled)
  record.friendly_name = credential_json['bindingDetail']['friendlyName']
  record.bind_status = credential_json['bindingDetail']['bindStatus']
  record.bind_time = credential_json['bindingDetail']['lastBindTime']
  record.last_authn_time = credential_json['bindingDetail']['lastAuthnTime']
  # Same as transaction_id?
  record.last_authn_id = credential_json['bindingDetail']['lastAuthnId']

  record.save()
  logger.debug('Record saved')
  return record


def process_token_credential(user_obj, credential_json):
  """Set up credential object ready to be saved.

  This should be used to record any credential that outputs a token which can
  be validated against the VIP API.
  """
  logger.debug('This is a token based credential')
  try:
    record = VipTokenCredential.objects.get(credential_id=credential_json['credentialId'] )
    logger.debug('Active record is %s, based on credential %s' % (record, credential_json['credentialId']))
  except Exception as ee:
    logger.debug('No record found for credential %s, creating a new VipTokenCredential' % credential_json['credentialId'])
    record = VipTokenCredential()
    record.push_enabled = False

  save_modified_record(record, user_obj, credential_json)



def process_push_credential(user_obj, credential_json):
  """Set up push credential object ready to be saved.

  This should be used to record any credential that uses out of band 'push'
  authentication to validate the user.
  Note that credentials of this kind can also have a token generating part so
  may appear in both credential types.
  """
  logger.debug('this is a push enabled credential')
  try:
    record = VipPushCredential.objects.get(credential_id=credential_json['credentialId'] )
    logger.debug('Active record is %s, based on credential %s' % (record, credential_json['credentialId']))
  except Exception as ee:
    logger.debug('No record found for credential %s, creating a new VipPushCredential' % credential_json['credentialId'])
    record = VipPushCredential()

  # Check attributes for useful information - platform and if push is enabled (rather than simply supported)
  for attrib in credential_json['pushAttributes']:
    if attrib['Key'] == 'PUSH_PLATFORM':
      record.attribute_platform = attrib['Value']
      logger.debug('Push platform is %s' % record.attribute_platform)

    if (attrib['Key'] == 'PUSH_ENABLED') :
      record.push_enabled = attrib['Value']
      logger.debug('Push enabled value is %s' % record.push_enabled)

  save_modified_record(record, user_obj, credential_json)


def update_user_credentials(supplied_data):
  """Update credential records in DB.

  Takes full user details from query_user_info and updates credential records in DB.
  Returns true or false to indicate success or failure.

  Note that this requires includePushAttributes=True, includeTokenInfo=True be
  passed to get_user_info (the default for query_user_info)
  """
  logger.debug('in update_user_credentials')
  if supplied_data:
    logger.debug('Full user details supplied, splitting out required information')
    try:
      user_credentials = supplied_data['credentialBindingDetail']
      user = utils.discover_user_from_email(supplied_data['userId'])
      logger.debug('supplied_data has been split in to user and user_credentials')
    except TypeError as te:
      logger.debug('Was passed invalid data ({0})'.format(supplied_data))
      return False
  else:
    logger.debug('Nothing supplied ({0})'.format(supplied_data))
    return False

  if not user:
    logger.debug('Unable to create or update credential without user object')
    return False

  if user_credentials:
    credentials_list = []
    logger.debug('looping %s credentials' % len(user_credentials))
    for current_credential in user_credentials:
      logger.debug('Working with credential %s' % current_credential['credentialId'])
      credentials_list.append(current_credential['credentialId'])

      # Only push capable platforms have values in pushAttributes
      if current_credential['pushAttributes']:
        push_cred = process_push_credential(user, current_credential)

      # I surmise this value roughly equates to 'has a token generating component'
      if current_credential['tokenInfo']['Adapter']:
        token_cred = process_token_credential(user, current_credential)
  else:
    logger.debug('No credentials to update')
    return True

  # Clean unknown tokens - this deletes any record from this user if it is missing from the API data.
  user.viptokencredential_set.exclude(credential_id__in=credentials_list).delete()
  user.vippushcredential_set.exclude(credential_id__in=credentials_list).delete()
  logger.debug('Pruned tokens no longer listed in API from database')

  # If we made it all the way to the end of this function without errors,
  return True

class VipPushCredential(VipBaseCredential):
  """Stores information about push credentials.

  Push credentials are those capable of receiving Symantec VIP push authentication
  request and displaying a notification to the user for action.
  """

  last_updated = models.DateTimeField(auto_now=True, verbose_name='Updated at')
  latest_transaction_id = models.CharField(max_length=30, editable=False)
  attribute_platform = models.CharField(max_length=30, editable=False)

  POLL_SLEEP_SECONDS = 10

  def generate_challenge(self):
    """Send request for a push to Symantec VIP servers.

    Request Symantec send a push authentication request to the specified users
    device and save the transaction id to the database

    This method runs self.save() to record the transaction id.
    """
    logger.debug('Calling send_user_auth_push and recording its transaction ID')
    auth_attempt = utils.send_user_auth_push(self.user.email)
    if auth_attempt is not None:
      logger.debug('Transaction ID: %s' % auth_attempt)
      self.latest_transaction_id = auth_attempt
      self.save(update_fields=['latest_transaction_id'])
      # Perform verification during challenge. Other option is overriding parts
      # of the submission form and this is, well, not better but acceptable
      verification_result = self.poll_push()
      return str('Sent (Check your device).')
    else:
      return str('An error occurred trying to send the push')

  def poll_push(self, *args):
    """Poll Symantec VIP service for a response to the push request."""
    if args:
      logger.debug('Unexpected arguments: {0}, skipping validation against this credential'.format(args))
      return False
    # Do we have a transaction ID to query?
    if not self.latest_transaction_id:
      return False

    # Sleep before running the query, user needs time to respond
    logger.debug('Sleeping for %s seconds' % self.POLL_SLEEP_SECONDS)
    time.sleep(self.POLL_SLEEP_SECONDS)

    logger.debug('Running poll_user_auth_push with transaction ID %s' % self.latest_transaction_id)
    # This returns True or False depending on the result
    poll_result = utils.poll_user_auth_push(self.latest_transaction_id)
    return poll_result


class VipTokenCredential(VipBaseCredential):
  """Stores information about token credentials.

  Token credentials are those which generate and display authentication codes
  which the user then enters in to a form and validates with Symantec.
  """

  token_code = models.CharField(max_length=30, default='')

  def verify_token(self, token):
    """Check with Symantec VIP service if this token code is valid."""
    logger.debug('recording token to db')
    self.token_code = token
    self.save()
    logger.debug("Calling validate_token_data with user {0} and token {1}".format(self.user.email, token))
    return utils.validate_token_data(self.user.email, token)


# Do these two have existing classes i can override?
# - possibly via twillio, django-otp-twilio
# This will have to wait until I have an SMS enabled VIP instance to play with
# class SmsCredential(VipBaseCredential):
#   """Records credentials which can receive SMS' via VIP"""
#   # needs to check if user has specified phone number. Bail if they haven't.
# if phone number in user profile, use it, else number passed as param to init, use it. else fail
#   pass

# class CallCredential(VipBaseCredential):
#   """Records credentials which can receive a call via VIP"""
#   # needs to check if user has specified phone number. Bail if they haven't.
# if phone number in user profile, use it, else number passed as param to init, use it. else fail
#   pass


