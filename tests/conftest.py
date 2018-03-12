"""
Configuration and set up for pytest.

This file contains some code that needs to be run before the tests are able to
succeed. At the moment that includes:
- Creating test users
- API mocking

"""

# https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-database-with-initial-test-data

import pytest

from django.contrib.auth.models import User

from otp_vip.models import VipUser

from datetime import datetime
import pytz

import api_data
from otp_vip import credential_models


# https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-database-with-initial-test-data
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Populate DB with users.

    Create a couple of users we can use for testing different parts of the codebase
    """
    with django_db_blocker.unblock():
       # Create required users
       User.objects.create(username='admin')
       # Currently created at top level of project
       # User.objects.create(username='karl', email='karl@example.com', first_name='Karl')
       User.objects.create(username='test_user', email='karl+testing@example.com')
       User.objects.create(username='another_test', email='karl+testing@example.com')
       User.objects.create(username='somename', email='foo@bar')
       # no user karl+testing-discourse@example.com, listed here as a warning

       User.objects.create(username='user_is_pro')

       # Instantiate an instance of VipUser, this user is pro so we'll need one that isn't too
       vu = VipUser()
       vu.user = User.objects.get(username='user_is_pro')
       # Use now, NotNull is on this but the date doesn't matter atm
       vu.vip_created_at = datetime.utcnow().replace(tzinfo=pytz.utc)
       vu.save()

       credential_models.update_user_credentials(api_data.get_user_info_credentials_json())


# TODO:
# Anything that is created during tests (for example credentials) to becreated here.


# TODO:
# Change SOAP API endpoints to pilot urls for testing.
# prefix all urls with pilot- eg
# https://pilot-userservices-auth.vip.symantec.com/vipuserservices/AuthenticationService_1_8

