The µbot D-Bus API
==================

A µbot instance will register a unique service name on the D-Bus of the form
``net.seveas.ubot.<botname here>``. The default is ``net.seveas.ubot.ubot``. It
exports several objects, the main bot and an object for each channel.

The name of the main bot is ``/net/seveas/ubot/<botname>`` and each channel is
exported as ``/net/seveas/ubot/<botname>/channel/<channel>``. As not all
characters that are valid in a channel name, are valid as D-Bus names,
non-alphabetic characters are replaced with an underscore (``_``) followed by
the ordinal number of the character. So, ``#`` is replaced ``_35`` and the
channel ``#microbot`` will be ``/net/seveas/ubot/ubot/channel/_35microbot``.

The methods and signals on bot objects are all part of the ``net.seveas.ubot``
interface. For methods on the channel objects, this is the
``net.seveas.ubot.channel`` interface.

Helpers must implemenet the ``net.seveas.ubot.helper`` interface, which
contains methods to query and control helpers. The standard helper libraries
implement this interface for you.

The ubot interface
------------------

For each signal and method, the D-Bus signature is displayed after the
parameters if it is not empty. The meaning of these signatures can be found in
the `D-Bus specification`_.

Signals
~~~~~~~

.. function:: connection_dropped()

   Sent whenever the current connection is dropped.

.. function:: connection_made(server, port) (si)

   Sent whenever a connection is made. Server and port are the server the bot
   is now connected to.
.. function:: net.seveas.ubot.exiting()

   This signal is sent when the bot is quitting. When helpers receive this
   signal, they should also terminate nicely.

.. function:: net.seveas.ubot.master_change(value) (b)

   Sent whenever the master status of the bot changes. Value is either ``True``
   or ``False`` and indicates whether the bot is now failover master or not.

.. function:: net.seveas.ubot.message_received(prefix, command, target, params) (sssas)

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
   
.. function:: net.seveas.ubot.message_sent(command, params) (sas)

   This signal is sent whenever a message is sent. Command and params have the
   same meaning as for :func:`message_received`. The target is part of the
   params.

.. function:: net.seveas.ubot.sync_complete()

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

.. get_channels:: (out: as)

   Returns a list of channels the bot has joined.

.. function:: get_helpers() (out: aas)

   Returns an array of 2-tuples ``(servicename, obejctname)`` that lists all
   active helpers.

.. function:: get_info() (out: a{sv})

   Returns a dictionary of information with the following keys:

   ========= =========
   Key       Signature
   --------- ---------
   connected b
   master    b
   nickname  b
   port      i
   server    s
   synced    b
   version   s
   ========= =========

   New entries may be added at any time.

.. function:: join(channel, key) (in: ss)

   Makes the bot try to join a channel. A key is required, use an empty string
   for channels that do not require a key to join.

.. function:: log(ident, level, msg) (sss)

   Log a message via the bots logger. 

.. function:: nick(newnick) (in: s)

   Change the bots nickname to the value of ``newnick``.

.. function:: quit(message) (in: s)

   Makes the bot quit IRC and shut itself down. This will also stop all the
   active helpers.

.. function:: say(user, message) (in: ss)
.. function:: do(user, message) (in: ss)
.. function:: slowsay(user, message) (in: ss)
.. function:: slowdo(user, message) (in: ss)

   This sends a message to a user. The ``do`` variants send the equivalent of a
   ``/me <message>``. The slow variants add the message to the end of the slow
   queue, which is only emptied when the normal queue is empty.

.. _`D-Bus specification`: http://dbus.freedesktop.org/doc/dbus-specification.html
