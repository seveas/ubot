#!/bin/bash
#
# Set up python/ruby/perl paths and dbus address so we run from source, but
# with config used by the installed ubot.
#
# Any arguments given to this script are interpreted as a command to run in
# this environment. If no arguments are given, it outputs the environment
# variables, usable by an eval, such as
#
# $ eval $(bin/rub_from_source.sh)

me=$(readlink -f "$0")
prefix=$(dirname $(dirname "$me"))
libdir="$prefix/lib"
plibdir="$prefix/plib"
rlibdir="$prefix/rlib"
sysconfdir="$HOME/.config"
sessionconf="$sysconfdir/ubot/session.conf"

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

DBUS_SESSION_BUS_ADDRESS=$(sed -n -e 's/^.*<listen>\(.*\)<\/listen>.*$/\1/p' < $sessionconf)

export PYTHONPATH PERL5LIB RUBYLIB DBUS_SESSION_BUS_PID DBUS_SESSION_BUS_ADDRESS

if [ $# != 0 ]; then
    "$@"
else
    echo export PYTHONPATH=\"$PYTHONPATH\"
    echo export PERL5LIB=\"$PERL5LIB\"
    echo export RUBYLIB=\"$RUBYLIB\"
    echo export DBUS_SESSION_BUS_PID=\"$DBUS_SESSION_BUS_PID\"
    echo export DBUS_SESSION_BUS_ADDRESS=\"$DBUS_SESSION_BUS_ADDRESS\"
fi
