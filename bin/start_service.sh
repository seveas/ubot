#!/bin/bash

dbus-send --print-reply \
    --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus \
    org.freedesktop.DBus.StartServiceByName \
    "string:$1" "uint32:0"
