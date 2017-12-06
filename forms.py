
from django import forms

from django_otp import credentials_for_user

from django_otp.forms import OTPTokenForm

class TokenForm(OTPTokenForm):
  """Form for any credential which involves text being submitted as part of
  verification"""

  def device_choices(self, user):
    token_credentials = []
    for d in devices_for_user(user):
      # This credential is not a push token
      if not d.is_interactive():
        token_credentials.append((d.persistent_id, d.name))
    return token_credentials



# For push credentials (not used, so silly name)
class PushForm(OTPTokenForm):
  """Form for any credential which involves OOB verification"""

  def device_choices(self, user):
    token_credentials = []
    for d in devices_for_user(user):
      # This credential is a push token
      if d.is_interactive():
        token_credentials.append((d.persistent_id, d.name))
    return token_credentials

# TODO: make form to add credentials
# - adding vip credentials needs a number of fields including a drop down selection for credential type
# - credential id must not contain spaces, azAZ09+# only

