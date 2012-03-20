#!/bin/bash

set -e
set -x

# Make sure we're clean
make distclean || true

# And now run all the automagic
aclocal
automake -ac
autoconf
./configure "$@"
