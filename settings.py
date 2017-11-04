# https://docs.djangoproject.com/en/1.8/topics/settings/#using-settings-in-python-code
# FIXME: Make this customisable / overridable. 
# FIXME: all thses /should/ be supplied by others, double bad to hard import in utils
VIP_CERTIFICATE_PUBLIC = 'django_otp_vip/certs/user_services_public.crt'
VIP_CERTIFICATE_PRIVATE = 'django_otp_vip/certs/user_services_decrypted.key'
VIP_WSDL_USERSERVICES_QUERY = 'django_otp_vip/wsdls/vipuserservices-query-1.8.wsdl'
VIP_WSDL_USERSERVICES_AUTH = 'django_otp_vip/wsdls/vipuserservices-auth-1.8.wsdl'
VIP_POLL_SLEEP_SECONDS = 10
VIP_POLL_SLEEP_MAX_COUNT = 10

