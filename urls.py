"""VIP URLs configuration."""
from django.conf.urls import url

from django_otp_vip.views import run_otp

urlpatterns = [
    url(r'^vip/login/?$', run_otp, name='otp_validate'),

    ]

