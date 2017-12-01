from collections import OrderedDict
from pprint import pprint
import inspect
import re
from batterytester.main_test.powerview_open_close_loop_test import PowerViewOpenCloseLoopTest

ATTR_DESCRIPTION = 'description'
ATTR_TYPE = 'type'
param_regex = re.compile(':param\s+(\S+)\s+(\S+):\s*(.*)')

a = param_regex.findall(inspect.getdoc(PowerViewOpenCloseLoopTest.__init__))

print(a)

_parameters = OrderedDict()
for param in a:
    _parameters[param[1]] = {ATTR_TYPE: param[0], ATTR_DESCRIPTION: param[2]}

val = inspect.signature(PowerViewOpenCloseLoopTest)
print(val)
#
for param in val.parameters.values():
    print(param.name)
    print(param.default)
    _para = _parameters[param.name]
    _para['default'] = param.default

_class_parameters = {}
for name, _param in _parameters.items():
    print(_param[ATTR_DESCRIPTION])

    _val = input(name)
