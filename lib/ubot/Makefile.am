SUBDIRS = web
pkgpythondir=${pythondir}/ubot
pkgpython_PYTHON = project_urls.py conf.py exceptions.py helper.py bot.py irc.py util.py autoconf.py __init__.py channel.py
dist_pkgpython_PYTHON = autoconf.py.in

autoconf.py: autoconf.py.in $(top_srcdir)/bin/substvars.sh
	chmod +x $(top_srcdir)/bin/substvars.sh
	$(top_srcdir)/bin/substvars.sh $< > $@

distclean-local:
	rm -f autoconf.py

dist-hook:
	rm -f $(distdir)/autoconf.py
