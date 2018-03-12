# Taken directly from
# https://stackoverflow.com/questions/18987051/how-do-i-unit-test-django-urls

from django.core.urlresolvers import reverse, resolve

# # No trailing slash
# @pytest.mark.django_db()
# def test_multi_factor_reverses():
#   """Reverse to login url
#   AFAIK you can't reverse to an url finishing in /
#   """
#   url = reverse('run_multi_factor')
#   assert url == '/vip/login'
# 
# @pytest.mark.django_db()
# def test_multi_factor_resolves():
#   resolver = resolve('/vip/login')
#   assert resolver.view_name == 'run_multi_factor'
# 
# # With trailing slash
# @pytest.mark.django_db()
# def test_multi_factor_resolves_with_slash():
#   resolver = resolve('/vip/login/')
#   assert resolver.view_name == 'run_multi_factor'

