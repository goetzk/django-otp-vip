"""Taken from django-otp at rev 8273d68 from 2017-12-16 then customised."""

# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.decorators import user_passes_test

from django_otp import user_has_device, _user_is_authenticated
from django_otp.conf import settings

from .models import VipUser


def otp_required(view=None, redirect_field_name='next', login_url=None, if_configured=True):
    """
    Customised version of django-otp otp_required decorator.

    Key changes:
    * if_configured is True by default not False
    * VIP specific check - does the DB record this user as eligible to use VIP
    * VIP specific check - does the DB record this user as active
    """
    if login_url is None:
        login_url = settings.OTP_LOGIN_URL

# TODO: add flag for 'if staff account, always 2fa' then add these checks with others below.
#   """Check if this user is allowed to use 2fa."""
#   logger.debug('Checking if %s may use 2FA' % user)
#
#   # Our additions
#   if user.is_superuser or user.is_staff:
#     logger.debug('%s is superuser or staff: 2FA enabled' % user)
#     # Site super users are required to have 2FA
#     return True

# FIXME: mind blown, will need to fix this later
    def test(user):
      """Add OTP VIP specific checks to ensure user should be using VIP."""
        logger.debug('Checking status for {0}'.format(u))
        vip_active = False
        try:
          if user.vipuser.status == 'ACTIVE':
            vip_active = True
          else:
            logger.debug('status is {0}, returning false'.format(user.vipuser.status))
            vip_active = False
        except VipUser.DoesNotExist as dne:
          logger.debug('{0} has no VipUser object so unable to check settings'.format(user))
          vip_active = False

        # Finally, perform original check
        return user.is_verified() or (if_configured and _user_is_authenticated(user) and not user_has_device(user))

    decorator = user_passes_test(test, login_url=login_url, redirect_field_name=redirect_field_name)

    return decorator if (view is None) else decorator(view)
