#!/bin/bash

set -e

# Make sure we're clean
make distclean || true

# And now run all the automagic
aclocal
automake -ac
autoconf
