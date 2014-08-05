import sys
from importlib import import_module

from config.unversioned import config_profile

config_module = import_module('{{ project_name }}.config.' + config_profile)
current_module = sys.modules[__name__]
for attribute in dir(config_module):
    if not (attribute.startswith('__') and attribute.endswith('__')):
        setattr(current_module, attribute, getattr(config_module, attribute))

from config.unversioned import *
