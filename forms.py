
from django import forms

from django_otp_vip.models import TokenDevice, PushDevice


class TokenForm(forms.ModelForm):
  """Form for any device which involves text being submitted as part of
  verification"""
  class Meta:
      model = TokenDevice
      fields = ['token_code']



class PushForm(forms.ModelForm):
  """Form for any device which does verification externally"""
  class Meta:
      model = PushDevice
      fields = []

