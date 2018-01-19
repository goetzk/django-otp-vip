"""VIP URLs configuration."""
from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from otp_vip.views import multi_factor

urlpatterns = [
    url(r'^login/?$', multi_factor, name='run_multi_factor'),
    # url(r'^check_mf_requirement$', multi_factor_check, {'multifactor_redirect': reverse_lazy('run_multi_factor'), 'direct_redirect': reverse_lazy('/') }, name='run_multifactor_requirement'),
    ]

