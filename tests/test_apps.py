
from otp_vip.apps import SymantecVipConfig

def test_app_config_class_name():
  assert SymantecVipConfig.name == 'otp_vip'

def test_app_config_class_docstring():
  assert SymantecVipConfig.__doc__ is not None

