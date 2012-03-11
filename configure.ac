AC_PREREQ([2.68])
AC_INIT([ubot], [1.0], [http://github.com/seveas/ubot])
AM_INIT_AUTOMAKE
AM_PATH_PYTHON([2.5])
AC_PATH_PROG([PERL], [perl])
AC_PATH_PROG([RUBY], [ruby])
AC_PATH_PROG([AWK], [awk])

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
          helpers/Makefile 
          lib/Makefile
          lib/ubot/Makefile
          lib/ubot/web/Makefile
          lib/ubot/web/control/Makefile
          lib/ubot/web/control/templates/Makefile
          lib/ubot/web/control/templates/registration/Makefile
          lib/ubot/web/control/templates/ubot/Makefile
          lib/ubot/web/control/templates/ubot/control/Makefile
          lib/ubot/web/media/Makefile
          lib/ubot/web/media/redmond/Makefile
          lib/ubot/web/media/redmond/images/Makefile
          plib/Makefile
          rlib/Makefile
          doc/Makefile)
