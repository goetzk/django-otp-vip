"""Custom forms for validating VIP credentials."""

from django import forms
from django.core.validators import RegexValidator

from django_otp import devices_for_user, user_has_device

from otp_vip import models

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



class RemoveCredentials(forms.Form):
  """Remove credential from API and user account.

  This form accepts input from the user then removes it from the VIP
  API and local DB
  """

  credentials_list = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                  to_field_name = 'credential_id',
                                  queryset=[])
  def __init__(self, *args, **kwargs):
    """Override init.

    This is needed so I can hack in a way to supply the user who submitted the
    form without doing a trip via the template and then having to re convert
    the supplied string to a user object.
    user = user object (required)
    """
    self.user = kwargs.pop('user', None)

    self.creds = self.user.viptokencredential_set.all()
    super(RemoveCredentials, self).__init__(*args, **kwargs)

    self.fields['credentials_list'].queryset = self.creds


