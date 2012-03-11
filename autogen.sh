#!/bin/bash

set -e

# Make sure we're clean
make clean || true

# Populate Makefile.am files in lib/ubot/
pushd lib/ubot > /dev/null
for d in $(find -type d); do
    pushd $d > /dev/null
    echo "SUBDIRS = $(find -maxdepth 1 -type d | sed -e 's!^\./!!' -e '/^\.$/d' | xargs echo)" > Makefile.am
    echo "pkgpythondir=\${pythondir}/${d/./ubot}" >> Makefile.am
    
    echo "pkgpython_PYTHON = $(find -maxdepth 1 -type f -not -name 'Makefile*' -and -not -name '*.py?' | sed -e 's!^\./!!' -e 's/\.in$//' | xargs echo)" >> Makefile.am
    if [ -e Makefile.am.extra ]; then
        cat Makefile.am.extra >> Makefile.am
    fi
    popd > /dev/null
done
popd > /dev/null

# Populate Makefile.am files in data/helpers/
pushd data/helpers > /dev/null
for d in $(find -type d); do
    pushd $d > /dev/null
    echo "SUBDIRS = $(find -maxdepth 1 -type d | sed -e 's!^\./!!' -e '/^\.$/d' | xargs echo)" > Makefile.am
    echo "pkgdatadir=\${datadir}/${d/./ubot/helpers}" >> Makefile.am
    echo "pkgdata_DATA = $(find -maxdepth 1 -type f -not -name 'Makefile*' | sed -e 's!^\./!!' | xargs echo)" >> Makefile.am
    popd > /dev/null
done
popd > /dev/null

# And now run all the automagic
aclocal
automake -ac
autoconf
./configure "$@"
