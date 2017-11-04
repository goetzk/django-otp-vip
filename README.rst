# TODO: rewrite, adding good docs along the way

django_otp_vip
==============

This Django app adds Symantec VIP integration to django-otp.


Install
=======
Currently only available in source form.

  git clone somewhere

Dependencies can be installed with `pip -r requirements.txt` once the project
has been cloned.

Setup
=====

django_otp_vip requires the following settings be available:

VIP_CERTIFICATE_PUBLIC and VIP_CERTIFICATE_PRIVATE
--------------------------------------------------

These are both extracted from a PEM file downloaded from Symantec VIP manager
(https://manager.vip.symantec.com/). To generate the certificate navigate
Account ->  Manage VIP Certificates (right hand side of screen) -> Request a
Certificate.

Once downloaded extract the two parts using openssl(1) or similar.


VIP_WSDL_USERSERVICES_QUERY and VIP_WSDL_USERSERVICES_AUTH
----------------------------------------------------------

These can be downloaded from Symantec VIP manager
(https://manager.vip.symantec.com/). Navigate Account -> Download Files (bottom
right of screen) -> Web_Services_API -> VIP_UserServicesWSDL.zip . Extract the
zip and place the files in a suitable location.


VIP_POLL_SLEEP_SECONDS
----------------------

How long should django_otp_vip wait between polls of the VIP endpoint when
checking for the status of a pushed authentication request.
The default is 10 seconds, a shorter time will lead to a quicker login for
users.


VIP_POLL_SLEEP_MAX_COUNT
------------------------

How many times should django_otp_vip poll the VIP endpoint for push
authentication before giving up on the users push.




See also
========

django-two-factor-authentication may be of interest if you are trying to use
django-otp (though currently lacks plugable modules like this one....)

python-vipaccess if you would like to avoid using Symantecs client software.
 - https://github.com/dlenski/python-vipaccess

