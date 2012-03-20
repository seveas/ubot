SUBDIRS = helpers
pkgdata_DATA = session.conf ubot.conf ubot_env.sh
dist_pkgdata_DATA = session.conf ubot.conf ubot_env.sh.in

ubot_env.sh: ubot_env.sh.in $(top_srcdir)/bin/substvars.sh
	chmod +x $(top_srcdir)/bin/substvars.sh
	$(top_srcdir)/bin/substvars.sh $< > $@

clean-local:
	rm -f ubot_env.sh
