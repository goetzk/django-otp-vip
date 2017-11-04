django_otp_vip
==============

This Django app adds Symantec VIP integration to django-otp.


Install
=======

Currently only available in source form.

  git clone https://gitlab.com/goetzk/django-otp-vip.git otp_vip

Dependencies can be installed with `pip -r requirements.txt` once the project
has been cloned.

Add to your projects INSTALLED_APPS and run migrations as required.

Setup
=====

otp_vip requires the following are available:

Public and Private halves of certificate to communicate with VIP
----------------------------------------------------------------

These are both extracted from a PEM file downloaded from Symantec VIP manager
(https://manager.vip.symantec.com/). To generate the certificate navigate
Account ->  Manage VIP Certificates (right hand side of screen) -> Request a
Certificate.

Once downloaded extract the two parts using openssl(1) or similar.

By default, otp_vip looks for them in:
- project_root/certs/user_services_public.crt
- project_root/certs/user_services_decrypted.key


WSDL files for VIP User Services
--------------------------------

These can be downloaded from Symantec VIP manager
(https://manager.vip.symantec.com/). Navigate Account -> Download Files (bottom
of list on right of screen) -> Web_Services_API -> VIP_UserServicesWSDL.zip .
Extract the zip and place the files in a suitable location.


By default, otp_vip looks for them in:
- project_root/wsdls/vipuserservices-auth-1.8.wsdl
- project_root/wsdls/vipuserservices-mgmt-1.8.wsdl
- project_root/wsdls/vipuserservices-query-1.8.wsdl


Push authentication poll details
--------------------------------

By default otp_vip will wait 10 seconds between polls of the VIP endpoint when
checking the status of a pushed authentication request.

The default for otp_vip is to poll the VIP endpoint for push authentication 10
times before giving up on the users push.

A shorter poll time will lead to a quicker login for users but lead to an
increased likelyhood of hitting the maximum count (both can be overriden in
code).

OTP_LOGIN_URL
-------------

Ensure OTP_LOGIN_URL is set to the location of the login view provided in this
project, we suggest '/vip/login'.


Features
========

Support for API calls required to
* Add/remove users
* Add/remove credentials
* Authenticate using push and tokens

Helper views to:
* Provide basic self service to users including adding/removing credentials
* Provide optional second factor - Only use VIP as where needed
* Require second factor check via middleware.

Usage
=====
Update your url patterns to include an entry such as this (which provides the
'vip/login' suggested above).

    url('^vip/', include('otp_vip.urls')),


Contributing
============

This project is hosted on GitLab (https://gitlab.com/goetzk/django-otp-vip),
with a public mirror on GitHub (https://github.com/goetzk/django-otp-vip) for
those who prefer it.


Tests
=====

While this project does have tests they are currently in a state of flux and
shouldn't be relied upon yet (Coverage from enabled tests is 50.85%).

See also
========

django-two-factor-authentication may be of interest if you are trying to use
django-otp (though currently lacks plugable modules like this one....)

python-vipaccess if you would like to avoid using Symantecs client software.
 - https://github.com/dlenski/python-vipaccess

