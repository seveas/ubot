Configuring µbot
================

µbot and its default helpers understand simple .ini files, parsed by
:mod:`ConfigParser` (python), :mod:`Config::INI::Reader` (perl) or
:mod:`ini.rb` (ruby). Example config files are shipped with µbot, below you
find a full reference.

Bot configuration
~~~~~~~~~~~~~~~~~
Bot configuration is placed in the `me` section of the main configuration
file (by default: :file:`~/.config/ubot/ubot.conf`). The following keys are
understood:

=================== ===========================================================
Key                 Description
=================== ===========================================================
nick1 ... nickN     The nickname for the bot. It will try all defined nicknames
                    sequentially until it finds one that it can use.
ident               The 'ident string' for the bot, traditionally the loginname
                    on the machine the IRC client runs on

realname            The 'real name' of the bot
server1 ... serverN A list of servers to try connecting to. This can be a
                    simple hostname, or a url like irc://freenode.net:6667 or
                    ircs://irc.freenode.net:6697 (SSL)
password            The irc server password to use. On many networks this is
                    only used by server admins.
busname             The unique identifier on the D-Bus for this bot. The
                    default is `ubot`, but you can change this and run multiple
                    bots on the same bus.
=================== ===========================================================

Here is a complete example::

 nick1    = MicroBot
 nick2    = Microbot`
 nick3    = MicroBot_
 ident    = mybot
 realname = µbot - ubot.seveas.net
 server1  = irc.freenode.net
 password = Secret

There is no limit to the number of nicks or servers  you can define, just make
sure they have consecutive, increasing numbers.

Logging
~~~~~~~
µbot uses the standard logging module for logging, which can be configured in
the main config file. A simple default configuration is shipped that writes raw
IRC messages and other log messages to separate logfiles. Helpers can use the
D-Bus API to log messages, thus ensuring consistent logs. For more information
about configuring logging, please read the `python logging documentation`_

.. _python logging documentation: http://docs.python.org/library/logging.html

Failover
~~~~~~~~
µbot supports a fairly simplistic coordinated failover protocol. Multiple
cooperating bots can act in a way that only one is ever active at a time. This
active role can automatically be taken over if the active bot leaves.

Two settings in the `me` section are important

=========== ============================================================
Key         Description
=========== ============================================================
controlchan Name of the failover coordination channel
priority    Priority of this bot in the group. The live bot with highest
            priority is the active bot.
=========== ============================================================

For each peer in the group of cooperating bots, an additional section needs to
be defined, named `peerN`. The sections need to be numbered in a consecutive
increasing order. Each section needs 2 keys:

========= ==========================================================================
Key       Description
========= ==========================================================================
nickmatch A regular expression that matches the nickname, ident and host of the peer
priority  Priority of this peer.
========= ==========================================================================

It is very important that priority and matching are configured in a consistent
way on *all* bots in the group for this to work properly.

Here is a complete example::

  [peer1]
  nickmatch = microbot2(`|_)?!(n|i)=ubot@seveas.net
  priority = 3

  [peer2]
  nickmatch = microbot3(`|_)?!(n|i)=ubot@ubot.seveas.net
  priority = 4
