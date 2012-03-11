rubylibdir = @RUBYLIBDIR@

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(rubylibdir)
	$(mkinstalldirs) $(DESTDIR)$(rubylibdir)/ubot
	$(INSTALL_DATA) ubot/irc.rb $(DESTDIR)$(rubylibdir)/ubot/irc.rb
	$(INSTALL_DATA) ubot/helper.rb $(DESTDIR)$(rubylibdir)/ubot/helper.rb

uninstall-local:
	$(RM) -f $(DESTDIR)$(rubylibdir)/ubot/helper.rb
	$(RM) -f $(DESTDIR)$(rubylibdir)/ubot/irc.rb
	$(RMDIR) $(DESTDIR)$(rubylibdir)/ubot
