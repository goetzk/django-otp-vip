"""Custom forms for validating VIP credentials."""

from django import forms
from django.core.validators import RegexValidator

from django_otp import devices_for_user, user_has_device

from django_otp_vip import models, credential_models, utils

from django_otp.forms import OTPTokenForm

class TokenForm(OTPTokenForm):
  """Token Form.

  Form for any credential which involves text being submitted as part of
  verification.
  """

  def device_choices(self, user):
    """Check which devices are compatible with this form."""
    token_credentials = []
    for d in devices_for_user(user):
      # This credential is not a push token
      if not d.is_interactive():
        token_credentials.append((d.persistent_id, d.name))
    return token_credentials



# For push credentials (not used, so silly name)
class PushForm(OTPTokenForm):
  """Form for any credential which involves OOB verification.

  OOB (Out Of Band) verification means it doesn't require the user submitting a
  code but can be a simple swipe like the Push compatible credentials.
  """

  def device_choices(self, user):
    """Check which devices are compatible with this form."""
    token_credentials = []
    for d in devices_for_user(user):
      # This credential is a push token
      if d.is_interactive():
        token_credentials.append((d.persistent_id, d.name))
    return token_credentials



# https://docs.djangoproject.com/en/1.8/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
class AddTokenCredential(forms.Form):
  """Add a new credential to API and user account.

  This form accepts input from the user then performs a refresh from the VIP
  API to gather the credentials full record from Symantec.
  """

  name = forms.CharField()
  credential_id = forms.CharField(validators=[
         # Validate token input early so it doesn't need cause an ugly SOAP validation error
         RegexValidator(
            regex='[0-9A-Za-z,#.*]{4,}',
            code='invalid_credential_id'
        ),
  ])


  def __init__(self, *args, **kwargs):
    """Override init.

    This is needed so I can hack in a way to supply the user who submitted the
    form without doing a trip via the template and then having to re convert
    the supplied string to a user object.
    """
    self.ident = kwargs.pop('user_id', None)
    super(AddTokenCredential, self).__init__(*args, **kwargs)

  def clean(self):
    """Override clean method.

    This is where I a making my calls to the API to add the credential then
    update our local DB.
    """
    # Then call the clean() method of the super  class
    cleaned_data = super(AddTokenCredential, self).clean()

    try:
      added_cred = utils.add_credential_to_vip(self.ident,
                                              cleaned_data['credential_id'],
                                              cleaned_data['name'])
      if not added_cred.status == '0000':
        raise forms.ValidationError('An error occurred ({1} - {0}) while adding {2} via the API.'.format(added_cred.statusMessage, added_cred.status, cleaned_data['credential_id']))
      # Attempt to update the DB based on API data now they have changed their tokens
      user_record_updated = utils.update_user_record(utils.query_user_info(self.ident))
      token_credential_updated = credential_models.update_user_credentials(utils.query_user_info(self.ident))

    except KeyError as ke:
      raise forms.ValidationError('Cleaned data was incomplete, unable to perform API call. Data supplied was {0}'.format(cleaned_data))


class RemoveCredentials(forms.Form):
  """Remove credential from API and user account.

  This form accepts input from the user then removes it from the VIP
  API and local DB
  """

  credentials_list = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                  to_field_name = 'name',
                                  queryset=[])
  def __init__(self, *args, **kwargs):
    """Override init.

    This is needed so I can hack in a way to supply the user who submitted the
    form without doing a trip via the template and then having to re convert
    the supplied string to a user object.
    user = user object (required)
    user_id = identifier used by VIP for this user, defaults to users email address.
    """
    self.user = kwargs.pop('user', None)
    self.ident = kwargs.pop('user_id', self.user.email)

    self.creds = self.user.viptokencredential_set.all()
    super(RemoveCredentials, self).__init__(*args, **kwargs)

    self.fields['credentials_list'].queryset = self.creds

  def clean(self):
    """Override clean method.

    This is where I a making my calls to the API to remove the credential then
    update our local DB.
    """
    cleaned_data = super(RemoveCredentials, self).clean()

    try:
      available_credentials = cleaned_data['credentials_list']
      print('gathered credentials from cleaned data')
    except KeyError as ke:
      available_credentials = []
      print('Unable to gather credentials from cleaned data')
      raise forms.ValidationError('Cleaned data was incomplete, data supplied was {0}'.format(cleaned_data))

    for removing_device in available_credentials:
      removed_cred = utils.remove_credential_from_vip(self.ident, removing_device.credential_id)
      if not removed_cred.status == '0000':
        raise forms.ValidationError('An error occurred ({1} - {0}) while removing {2} from {3} via the API.'.format(removed_cred.statusMessage, removed_cred.status, removing_device.credential_id, self.ident ))
      else:
        # Only remove from DB if successfully removed from API.
        token_credential_updated = credential_models.update_user_credentials(utils.query_user_info(self.ident))


# TODO: Fix this, it isn't updating the DB. (nor is it reading from the db)
class Change2faSetting(forms.Form):
  """Manage multifactor_wanted setting in VipUser."""

  multifactor_enabled = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    """Override init.

    This is needed so I can hack in a way to supply the user who submitted the
    form without doing a trip via the template and then having to re convert
    the supplied string to a user object.
    """
    self.user = kwargs.pop('user', None)
    super(Change2faSetting, self).__init__(*args, **kwargs)

  def clean(self):
    """Override clean method.

    Ensure this user has a usable credential ('device' in django-otp speak).
    """
    cleaned_data = super(Change2faSetting, self).clean()

    if not user_has_device(self.user):
      print('no devices here')
      forms.ValidationError('You must have at least one credential to enable Multifactor login')
    else:
      try:
        self.users_vipuser = models.VipUser.objects.get(user=self.user)
        print('vipuser found')
      except models.VipUser.DoesNotExist as dne:
        utils.update_user_record(utils.query_user_info(self.user.email))
        self.users_vipuser = models.VipUser.objects.get(user=self.user)
        print('vipuser created')
      self.users_vipuser.multifactor_wanted = cleaned_data['multifactor_enabled']
      self.users_vipuser.save()

