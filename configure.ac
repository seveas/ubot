AC_PREREQ([2.68])
AC_INIT([ubot], [0.9], [http://github.com/seveas/ubot])
AM_INIT_AUTOMAKE
AM_PATH_PYTHON([2.5])
AC_PATH_PROG([PERL], [perl])
AC_PATH_PROG([RUBY], [ruby])
AC_PROG_AWK
AC_PROG_SED

RUBYLIBDIR="${prefix}/lib/site_ruby"
for dir1 in ${prefix}/lib/ruby ${prefix}/lib; do
    for dir2 in site_ruby vendor_ruby; do
        if test -e "$dir1/$dir2"; then
            RUBYLIBDIR="$dir1/$dir2"
        fi
    done
done
AC_SUBST(RUBYLIBDIR)

AC_OUTPUT(Makefile 
          bin/Makefile 
          bin/substvars.sh
          helpers/Makefile 
          lib/Makefile
          lib/ubot/Makefile
          lib/ubot/web/Makefile
          lib/ubot/web/control/Makefile
          lib/ubot/web/control/templates/Makefile
          lib/ubot/web/control/templates/registration/Makefile
          lib/ubot/web/control/templates/ubot/Makefile
          lib/ubot/web/control/templates/ubot/control/Makefile
          lib/ubot/web/encyclopedia/Makefile
          lib/ubot/web/media/Makefile
          lib/ubot/web/media/redmond/Makefile
          lib/ubot/web/media/redmond/images/Makefile
          plib/Makefile
          rlib/Makefile
          doc/Makefile
          data/Makefile
          data/helpers/Makefile
          data/helpers/agenda/Makefile
          data/helpers/bugtracker/Makefile
          data/helpers/encyclopedia/Makefile
          data/helpers/noroot/Makefile
          data/helpers/pmrelay/Makefile
          data/helpers/p2000/Makefile
          data/helpers/isup/Makefile
          data/helpers/mess/Makefile
          data/helpers/lart/Makefile
          data/helpers/users/Makefile)

if test "$prefix" != "/usr"; then
    pkgdatadir=$(eval "echo $datarootdir")/ubot
    cat <<EOF
===========================================================================
You have configured ubot to install into $prefix

This makes is slightly difficult for python/perl/ruby to
find the ubot libraries. Please source $pkgdatadir/ubot_env.sh
from your ~/.bashrc to make this a bit easier.
===========================================================================
EOF
fi
