import os
import re
import sys

_invalid_dbus_path_re = re.compile(r'[^a-zA-Z0-9]')
def escape_object_path(val):
    return _invalid_dbus_path_re.sub(lambda x: '_' + str(ord(x.group(0))), val)

def icmp(val1, val2):
    return cmp(val1.lower(), val2.lower())
__builtins__['icmp'] = icmp

def become_daemon():
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    os.setsid()
    os.chdir("/")

    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        os._exit(1)

    print "%s daemon running, PID %d" % (os.path.basename(sys.argv[0]), os.getpid())

    devnull = open('/dev/null', 'r')
    os.dup2(devnull.fileno(), sys.stdin.fileno())
    os.dup2(devnull.fileno(), sys.stdout.fileno())
    os.dup2(devnull.fileno(), sys.stderr.fileno())
    sys.stdout = sys.stderr = devnull
