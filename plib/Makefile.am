perllibdir = $(prefix)/lib/perl5/

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(perllibdir)
	$(mkinstalldirs) $(DESTDIR)$(perllibdir)/Ubot
	$(INSTALL_DATA) Ubot/Irc.pm $(DESTDIR)$(perllibdir)/Ubot/Irc.pm
	$(INSTALL_DATA) Ubot/Helper.pm $(DESTDIR)$(perllibdir)/Ubot/Helper.pm

uninstall-local:
	$(RM) -f $(DESTDIR)$(perllibdir)/Ubot/Helper.pm
	$(RM) -f $(DESTDIR)$(perllibdir)/Ubot/Irc.pm
	$(RMDIR) $(DESTDIR)$(perllibdir)/Ubot
