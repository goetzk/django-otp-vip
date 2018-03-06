"""VIP URLs configuration."""
from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from otp_vip.views import multi_factor

urlpatterns = [
    url(r'^login/?$', multi_factor, name='run_multi_factor'),
    # url(r'^managevip$', manage_two_factor, { 'template': 'myvip.html' }, name='manage_vip'),
    ]

