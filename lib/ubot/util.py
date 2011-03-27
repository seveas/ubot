import re

_invalid_dbus_path_re = re.compile(r'[^a-zA-Z0-9]')
def escape_object_path(val):
    return _invalid_dbus_path_re.sub(lambda x: '_' + str(ord(x.group(0))), val)

def icmp(val1, val2):
    return cmp(val1.lower(), val2.lower())
__builtins__['icmp'] = icmp
