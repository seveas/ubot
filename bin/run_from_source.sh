#!/bin/bash
#
# Generate *.service and session.conf with absolute paths

me="$0"
cwd=$(pwd)
if [ ${me:0:1} = '.' ]; then
    me="$cwd${me:1}"
fi
if [ ${me:0:1} != '/' ]; then
    me="$cwd/$me"
fi
prefix=$(dirname $(dirname "$me"))
libdir="$prefix/lib"
plibdir="$prefix/plib"
rlibdir="$prefix/rlib"
sysconfdir="$HOME/.config"
sessionconf="$sysconfdir/ubot/session.conf"
localstatedir=$HOME/.local/share

mkdir -p "$sysconfdir/ubot/services"
for conf in $(find "$prefix/etc" -type f -name '*.in'); do
    realconf="$sysconfdir/ubot${conf#$prefix/etc}"
    realconf="${realconf%.in}"
    sed -e "s!@PREFIX@!$prefix!" \
        -e "s!@LOCALSTATEDIR@!$localstatedir!" \
        -e "s!@SYSCONFDIR@!$sysconfdir!" < "$conf" > "$realconf"
done

if [ -z "$PYTHONPATH" ]; then
    PYTHONPATH="$libdir"
else
    PYTHONPATH="$libdir:$PYTHONPATH"
fi
if [ -z "$PERL5LIB" ]; then
    PERL5LIB="$plibdir"
else
    PERL5LIB="$plibdir:$PERL5LIB"
fi
if [ -z "$RUBYLIB" ]; then
    RUBYLIB="$rlibdir"
else
    RUBYLIB="$rlibdir:$RUBYLIB"
fi
pid=$(pgrep -f $sessionconf)
if [ -z "$pid" ]; then
    eval $(dbus-launch --config-file $sessionconf)
else
    address=$(sed -n -e 's/^.*<listen>\(.*\)<\/listen>.*$/\1/p' < $sessionconf)
    DBUS_SESSION_BUS_PID=$pid
    DBUS_SESSION_BUS_ADDRESS=$address
fi
if [ $# != 0 ]; then
    export PYTHONPATH PERL5LIB RUBYLIB DBUS_SESSION_BUS_PID DBUS_SESSION_BUS_ADDRESS
    "$@"
else
    echo export PYTHONPATH=\"$PYTHONPATH\"
    echo export PERL5LIB=\"$PERL5LIB\"
    echo export RUBYLIB=\"$RUBYLIB\"
    echo export DBUS_SESSION_BUS_PID=\"$DBUS_SESSION_BUS_PID\"
    echo export DBUS_SESSION_BUS_ADDRESS=\"$DBUS_SESSION_BUS_ADDRESS\"
fi
