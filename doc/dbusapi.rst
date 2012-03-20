The µbot D-Bus API
==================

A µbot instance will register a unique service name on the D-Bus of the form
``net.seveas.ubot.<botname>``. The default is ``net.seveas.ubot.ubot``. It
exports several objects: the main bot and an object for each channel.

The name of the main bot is ``/net/seveas/ubot/<botname>`` and each channel is
exported as ``/net/seveas/ubot/<botname>/channel/<channel>``. As not all
characters that are valid in a channel name are valid as D-Bus names,
non-alphabetic characters are replaced with an underscore (``_``) followed by
the ordinal number of the character. So, ``#`` is replaced ``_35`` and the
channel ``#microbot`` will be ``/net/seveas/ubot/ubot/channel/_35microbot``.

The methods and signals on bot objects are all part of the
``net.seveas.ubot.bot`` interface. For methods on the channel objects, this is
the ``net.seveas.ubot.channel`` interface.

Helpers must implement the ``net.seveas.ubot.helper`` interface, which contains
methods to query and control helpers. The standard helper libraries implement
this interface for you.

The net.seveas.ubot.bot interface
---------------------------------

For each signal and method, the D-Bus signature is displayed after the
parameters if it is not empty. The meaning of these signatures can be found in
the `D-Bus specification`_.

Signals
~~~~~~~

.. function:: connection_dropped()

   Sent whenever the current connection is dropped.

.. function:: connection_established(server, port) (si)

   Sent whenever a connection is made. Server and port are the server the bot
   is now connected to.
.. function:: exiting()

   This signal is sent when the bot is quitting. When helpers receive this
   signal, they should also terminate nicely.

.. function:: master_change(value) (b)

   Sent whenever the master status of the bot changes. Value is either ``True``
   or ``False`` and indicates whether the bot is now failover master or not.

.. function:: message_received(prefix, command, target, params) (sssas)

   This signal is sent whenever a signal is received. The prefix is the
   nick!ident\@host string of the user who sent the message, command is the
   command used (such as ``PRIVMSG``), target is the target of the message and
   params is the parameters. An example set of arguments:

   ======= =========================================
   prefix  ``u'Seveas!ubuntu@ubuntu/member/seveas'``
   command ``u'PRIVMSG'``
   target  ``u'#microbot'``
   params  ``[u'Hello, world!']``
   ======= =========================================
   
.. function:: message_sent(command, params) (sas)

   This signal is sent whenever a message is sent. Command and params have the
   same meaning as for :func:`message_received`. The target is part of the
   params.

.. function:: sync_complete()

   This signal is sent when the bot has joined all its configured channels
   after joining and all channel info for this channel has been received. The
   bot will also have assumed failover master role if it should be the master.

Methods
~~~~~~~

.. function:: register_helper(service, path) (in: so)

   Helpers must call this function to register themselves with the bot. This
   way they will show up in the webadmin and the bot can control them.
   Unregistering is not needed (or possible, for that matter), as the bot
   detects when helpers disconnect from the bus.

.. function:: get_channels (out: as)

   Returns a list of channels the bot has joined.

.. function:: get_helpers() (out: aas)

   Returns an array of 2-tuples ``(servicename, objectname)`` that lists all
   active helpers.

.. function:: get_info() (out: a{sv})

   Returns a dictionary of information with the following keys:

   ============== =========
   Key            Signature
   -------------- ---------
   connected      b
   master         b
   nickname       b
   port           i
   server         s
   server_version s
   synced         b
   version        s
   ============== =========

   New entries may be added at any time.

.. function:: join(channel, key) (in: ss)

   Makes the bot try to join a channel. A key is required, use an empty string
   for channels that do not require a key to join.

.. function:: list_channels(nick) (in: s)

   Get all channels a certain nickname can be found in.

.. function:: log(ident, level, msg) (in: sss)

   Log a message via the bots logger. 

.. function:: nick(newnick) (in: s)

   Change the bots nickname to the value of ``newnick``.

.. function:: quit(message) (in: s)

   Makes the bot quit IRC and shut itself down. This will also stop all the
   active helpers.

.. function:: rawmsg(command, params) (in: sas)

   Send a raw message with parameters.

.. function:: say(user, message) (in: ss)
.. function:: do(user, message) (in: ss)
.. function:: slowsay(user, message) (in: ss)
.. function:: slowdo(user, message) (in: ss)

   This sends a message to a user. The ``do`` variants send the equivalent of a
   ``/me <message>``. The slow variants add the message to the end of the slow
   queue, which is only emptied when the normal queue is empty.

The net.seveas.ubot.channel interface
-------------------------------------

For each signal and method, the D-Bus signature is displayed after the
parameters if it is not empty. The meaning of these signatures can be found in
the `D-Bus specification`_.

Signals
~~~~~~~
None yet.

Methods
~~~~~~~

.. function:: get_key() (out: s)

   Gets the channel key.

.. function:: get_limit() (out: i)

   Gets the channel occupancy limit.

.. function:: get_mode() (out: as)

   Returns a list of mode characters. This never includes mode l or k, or thier
   values (channel limit and key).

.. function:: get_nicks() (out: a{ss})

   This returns a dictionary mapping nicknames to mode characters. Mode
   characters are ``@`` for ops, and ``+`` for voice. Beware, both can be
   present for the same user, in any order.

.. function:: get_topic() (out: s)

   Gets the channel topic.

.. function:: invite(nick) (in: s)

   Invite a user to the channel

.. function:: kick(nick, msg) (in: ss)

   Kick a user from the channel.

.. function:: part(partmsg) (in: s)

   Leave the channel

.. function:: say(message) (in: ss)
.. function:: do(message) (in: ss)
.. function:: slowsay(message) (in: ss)
.. function:: slowdo(message) (in: ss)

   This sends a message to the channel. The ``do`` variants send the equivalent
   of a ``/me <message>``. The slow variants add the message to the end of the
   slow queue, which is only emptied when the normal queue is empty.

.. function:: set_mode(mode) (in: s)

   This sends a mode command to the server. mode is passed raw, so it can
   contain modes, bans channel limit and channel key.

.. function:: set_topic(topic) (in: s)

   This sets the channel topic.


The net.seveas.ubot.helper interface
------------------------------------

All helpers must implement the full helper interface. There are only a few
methods, and the helper libraries shipped with µbot implement them all for you.

For each signal and method, the D-Bus signature is displayed after the
parameters if it is not empty. The meaning of these signatures can be found in
the `D-Bus specification`_.

Signals
~~~~~~~
None yet.

Methods
~~~~~~~

.. function:: quit()

   The helper must exit when this is called.

.. function:: get_info() (out: a{ss})

   Must returns a dictionary of information with the following keys:

   * name
   * description
   * version
   * url
   * author_name
   * author_nick
   * author_network
   * author_email

   Note that all values must be strings.

.. _`D-Bus specification`: http://dbus.freedesktop.org/doc/dbus-specification.html
