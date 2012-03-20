Running µbot
============

Starting the bot
----------------
The first time you run µbot, it will prompt you for basic configuration
variables. It will then start its own D-Bus daemon (if it's not yet running)
and then launch itself into the background. It will log into logfiles in
:file:`~/.local/share/ubot` and not output anything on screen after startup.

To see the status of the bot, you can use the :program:`ubot send` command ::

  $ ubot send get_info
  Calling get_info with arguments []
  {'connected': True,
   'master': True,
   'nickname': 'MicroBot',
   'port': 6667,
   'server': 'irc.freenode.net',
   'server_version': 'ircd-seven-1.1.3',
   'synced': True,
   'version': '0.0.1'}

µbot will automatically join its control channel and wait for further instructions.

Starting helpers
----------------

Helpers can also be started via the main :program:`ubot` utility. They will be
started by the D-Bus daemon and run as services. Logging is done via the µbot
instance they talk to, and thus will end up in the same logfiles. As an
example, here is how you start the lart helper ::

  $ ubot start lart

If you want to run a helper manually, you can look at the relevant .service
file in :file:`~/.config/ubot/services/` to find out the commands to use.

Administering the bot on the command line
-----------------------------------------
µbot can be conveniently administered from the command line. with the command
:program:`ubot send`, you can send the bot any command that can be sent via the
:doc:`D-Bus API <dbusapi>`. Here is an example that makes the bot join a
channel without passphrase. ::

  $ ubot send get_channels
  Calling get_channels with arguments []
  ['#microbot']
  $ ubot send join '#microbot-test' ''
  Calling join with arguments ['#microbot-test', '']
  $ ubot send get_channels
  Calling get_channels with arguments []
  ['#microbot', '#microbot-test']

Please read the D-Bus API documentation to get a full overview of what
:program:`ubot send` can do for you.

The µbot web interface
----------------------

The µbot web interface is a django application that can integrate with an
existing django environment or be run standalone. The standalone server
requires no additional configuration and can be started with :program:`ubot
instaweb`. If you wish to include the command interface in your existing django
application, you will need to set the :envvar:`DBUS_SESSION_BUS_ADDRESS` in
your settings.py and add :py:mod:`ubot.control` to your
:envvar:`INSTALLED_APPS`.

If you use the instaweb server, you can go to http://127.0.0.1:8000/control/ to
control your bots. You will need to give yourself administrator access to the
bot first by visiting http://127.0.0.1/admin/

With this web interface you can make your µbot do things such as join and part
channels or send messages. You can also start and stop helpers from there.
