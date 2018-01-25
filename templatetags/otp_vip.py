"""OTP/VIP related template tags."""

from django import template
register = template.Library()

@register.assignment_tag
def available_token_credentials(user):
  """Return list of all Token credentials associated with the user."""
  token_list = user.viptokencredential_set.all().values_list('name', 'credential_id', 'last_authn_time')
  return token_list

@register.assignment_tag
def available_push_credentials(user):
  """Return list of all Push credentials associated with the user."""
  push_list = user.vippushcredential_set.all().values_list('name', 'credential_id', 'last_authn_time')
  return push_list

