
# Further reading
"""
http://pytest-django.readthedocs.io/en/latest/helpers.html#examples
http://engineroom.trackmaven.com/blog/using-pytest-with-django/ *maybe*

"""

from django.contrib.auth.models import User

from otp_vip.models import VipUser

import pytest


# @pytest.mark.django_db()
# def test_vip_user_unicode_user_without_vip_user_id():
#   vu = VipUser.objects.get(user=User.objects.get(username='user_is_pro'))
#   assert vu.__unicode__() == '{0} ({1})'.format(vu.user.username, 'False')
# 
# @pytest.mark.django_db()
# def test_vip_user_unicode_user_with_vip_user_id():
#   vu = VipUser.objects.get(user=User.objects.get(username='user_is_pro'))
#   vu.vip_user_id = 'madeup'
#   assert vu.__unicode__() == '{0} ({1})'.format(vu.user.username, vu.vip_user_id)
# 
