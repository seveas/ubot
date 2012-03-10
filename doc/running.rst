Running µbot
============

Starting the bot
----------------
µbot can be started from the web interface or from the terminal. For now, let's
use the terminal and we'll worry about the web interface later. First we need
to start our special D-Bus daemon and set up our environment.

::
  dennis@lightning:~/ubot$ eval $(bin/run_from_source.sh)
  dennis@lightning:~/ubot$ 

Now that D-Bus is running, we can start the bot. Because µbot ships with
service files that are installed alongside the D-Bus configuration, we can
either let D-Bus start the bot in the background, or run it ourselves.

Starting automatically:

::
  dennis@lightning:~/ubot$ bin/ubot-send get_info
  Calling get_info with arguments []
  dbus.Dictionary({dbus.String(u'server'):
  [... more output omitted ...]

Running it manually:

::
  dennis@lightning:~/ubot$ bin/ubot -v -c ~/.config/ubot/ubot.conf

Starting helpers
----------------
Like µbot itself, helpers also register their own unique bus name and can be
started in the same way: via the web interface, via the command line by talking
to the D-Bus daemon or starting the helper manually. The easiest way is manually:

::
  dennis@lightning:~/ubot$ helpers/lart -c ~/.config/ubot/lart.conf

Administering the bot
---------------------
The `ubot-send` tool shipped with µbot allows you to control the bot via the
command line. It is a very simple wrapper around the µbot :doc:`D-Bus API
<dbusapi>`. Here is an example that makes the bot join a channel without
passphrase.

::
  dennis@lightning:~/code/ubot-1$ bin/ubot-send get_channels
  Calling get_channels with arguments []
  dbus.Array([dbus.String(u'#microbot'), dbus.String(u'#microbot-off')], signature=dbus.Signature('s'))
  dennis@lightning:~/code/ubot-1$ bin/ubot-send  join '#microbot-test' ''
  Calling join with arguments ['#microbot-test', '']
  None
  dennis@lightning:~/code/ubot-1$ bin/ubot-send get_channels
  Calling get_channels with arguments []
  dbus.Array([dbus.String(u'#microbot-test'), dbus.String(u'#microbot'), dbus.String(u'#microbot-off')], signature=dbus.Signature('s'))

As you can see, it is a very thin layer above the code, so this is not
recommended for daily use. However, it is useful for integrating with
shellscripts and other external tools.
