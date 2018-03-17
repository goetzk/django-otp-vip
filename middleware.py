# Set up logging first thing
import logging
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django_otp import user_has_device, _user_is_anonymous, _user_is_authenticated

# https://stackoverflow.com/questions/2916966/non-global-middleware-in-django
# was the best help I found here, with several good posts.

class MandatoryOtpMiddleware(object):
  """Ensure all users configured for OTP are using it.

  This middleware uses data set by django_otp.middleware.OTPMiddleware so must
  be installed after it in Django middleware settings.
  """

  otp_login_url = reverse('run_multi_factor') # This should probably be settings.OTP_LOGIN
  excluded_urls_list = ['/accounts/logout/', otp_login_url]

  def user_must_authenticate(self,request):
    """Check to run against user on each request.

    Note that this will slow down EVERY request it is called on, so try to keep
    it snappy!
    If you need to override the behaviour of this function you should consider
    subclassing MandatoryOtpMiddleware and running this via Super() to preserve
    the existing behaviour.

    Return True if user must authenticate, False if they are fine.
    """

    # If they have at least one device they should be logged in via OTP
    if user_has_device(request.user):
      if not request.user.is_verified():
        logger.debug('{0} is authenticated but not verified.'.format(request.user))
        return True
      # else, they are verified and are OK
    # else they have no device; they don't need to have OTP
    return False

  def process_request(self, request):
    """
    Automatically ensure users who should be logged in via OTP are.
    """
    current_url = request.path_info

    # We don't need to worry about annon users
    if _user_is_anonymous(request.user):
      return None

    # A select few views can't be captured. For example
    # * Logout means we can never leave the site
    # * OTP login means a redirect loop when viewing the otp login url.
    # if current_url in self.excluded_urls_list:
    # FIXME: This is really poor and should be fixed. Something like
    # https://stackoverflow.com/a/30197797 will help, but this is still a hack.
    for exclude_url in self.excluded_urls_list:
      test_result = current_url.find(exclude_url)
      if test_result >= 0:
        logger.debug('Currently requested url ({0}) matches {1} in excluded urls list ({2})'.format(current_url, exclude_url, self.excluded_urls_list))
        return None

    logger.debug('{0} visited {1} which is not excluded'.format(request.user, current_url))
    # Only need to check in more detail if they are logged in
    if _user_is_authenticated(request.user):
      # Run our checks and redirect code, it lives apart to be easily overridden.
      if self.user_must_authenticate(request):
        # Returned true, send the user away
        logger.debug('{0} needs to supply their second factor. Redirecting to {1}'.format(request.user, self.otp_login_url))
        return HttpResponseRedirect(self.otp_login_url)

    # If nothing else causes a redirect, return None to finish off
    return None

