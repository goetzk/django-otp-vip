"""VIP URLs configuration."""
from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from otp_vip.views import multi_factor, check_verification, manage_two_factor

urlpatterns = [
    url(r'^login/?$', multi_factor, name='run_multi_factor'),
    url(r'^test_multi$', check_verification, name='test_multi'),
    url(r'^managevip$', manage_two_factor, { 'template': 'myvip.html' }, name='manage_vip'),
    ]

