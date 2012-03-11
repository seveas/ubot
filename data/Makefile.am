SUBDIRS = helpers
pkgdata_DATA = session.conf ubot.conf ubot_env.sh

ubot_env.sh: ubot_env.sh.in
	chmod +x $(top_srcdir)/bin/substvars.sh
	$(top_srcdir)/bin/substvars.sh $< > $@

clean-local:
	rm -f ubot_env.sh
