
from django import forms

from django_otp import devices_for_user

from django_otp.forms import OTPTokenForm

class TokenForm(OTPTokenForm):
  """Form for any device which involves text being submitted as part of
  verification"""

  def device_choices(self, user):
    token_devices = []
    for d in devices_for_user(user):
      # This device is not a push token
      if not d.is_interactive():
        token_devices.append((d.persistent_id, d.name))
    return token_devices



# For push devices (not used, so silly name)
class PushForm(OTPTokenForm):
  """Form for any device which involves OOB verification"""

  def device_choices(self, user):
    token_devices = []
    for d in devices_for_user(user):
      # This device is a push token
      if d.is_interactive():
        token_devices.append((d.persistent_id, d.name))
    return token_devices

# TODO: make form to add devices
# - adding vip credentials needs a number of fields including a drop down selection for device type
# - credential id must not contain spaces, azAZ09+# only

