#!/bin/bash

set -e

# Populate Makefile.am files in lib/
pushd lib/ubot > /dev/null
for d in $(find -type d); do
    pushd $d > /dev/null
    echo "SUBDIRS = $(find -maxdepth 1 -type d | sed -e 's!^\./!!' -e '/^\.$/d' | xargs echo)" > Makefile.am
   echo "pkgpythondir=\${pythondir}/${d/./ubot}" >> Makefile.am
    
    echo "pkgpython_PYTHON = $(find -maxdepth 1 -type f -not -name 'Makefile*' | sed -e 's!^\./!!' | xargs echo)" >> Makefile.am
    popd > /dev/null
done
popd > /dev/null

# And now run all the automagic
aclocal
automake -ac
autoconf
./configure "$@"
