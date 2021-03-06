Ruby helper library
===================

The ruby helper library wraps the D-Bus API in a way that makes it really
easy to write helpers. Each helper is a subclass of the :class:`Ubot::Helper`
module and deals with :class:`InMessage` objects. The library also provides a
standard way of handling configuration and command-line arguments.

Hello, world! example
---------------------

The following is a complete helper that responds to ``@hello`` with ``Hello,
you``

.. literalinclude:: ../helpers/rb_hello
   :language: ruby
   :linenos:

As you can see, no D-Bus programming needed, you don't even need to write a
mainloop! All you need to write are a dictionary with information and the code
that actually responds to the messages. The :func:`add_options` and
:func:`handle_options` definitions are there for demonstration only, usually
you would place this in a configuration file.

The ubot.helper module
----------------------

This module defines the helper base classes you need to subclass to write a
helper.

.. class:: Ubot::Helper

  This is the master class, it contains most of the functionality and all other
  helper base classes subclass it.

  Helper objects have a few useful attributes

  .. attribute:: master

     Whether the bot is currently failover master.

  .. attribute:: synced

     Whether the bot is currently fully synced (joined all channels and has all
     channel info)

  .. attribute:: conf

     A ConfigParser object that has read the config for the helper.

  .. attribute:: bot

     A D-Bus proxy object for the bot that follows the :doc:`D-Bus ubot
     interface <dbusapi>`

  .. attribute:: channels

     A dictionary that maps channel names to D-Bus proxy objects that follow
     the :doc:`D-Bus channel interface <dbusapi>`

  .. attribute:: nickname

     The nickname of the bot.

  The actual running of the helper class is accomplished by calling the
  classmethod :meth:`run`. You should not override this method. Instead, you
  can provide hooks for it to call.

  .. function:: run

     Run the helper. It does a few things:

     * Parse commandline arguments
     * Let helpers handle commandline arguments
     * Set up a mainloop
     * Run the mainloop
     * Run any teardown functions.

     To influence the behaviour of run, there are three hooks you can provide:
     :func:`add_options`, :func:`handle_options` and :func:`exit`.

  .. function:: add_options(self, parser)

     This function is passed an ``OptionParser`` instance as argument.  It can
     add extra commandline arguments. You should always call the superclass'
     add_options method as it defines several arguments as well.

     Defined arguments:

     ====== ============= ==============================
     Short  Long version  Default
     ====== ============= ==============================
     ``-a`` ``--address`` tcp\:host=localhost,port=11235
     ``-n`` ``--name``    The name of the class [1]_
     ``-c`` ``--config``  None
     ====== ============= ==============================

     .. [1] The suffixes ``Responder``, ``Commander``, ``Notifier`` and
        ``Listener`` are removed from the class name in this case.

  .. function:: handle_options(self, opts)

     This function is passed the opts object as set up by ``parser.parse!`` and
     responsible for setting up the helper. If you override this method, make
     sure you call the superclass' method early on as it does some essential
     initialization like reading the configuration and setting the :attr:`bot`
     attribute.

     Configuration keys inspected:

     ======= ==================
     Key     Default
     ======= ==================
     botname ubot
     busname name of the helper
     ======= ==================

     The botname is the D-Bus name of the bot as defined in the bots
     configuration.

  .. function:: exit(self)

     This function is called after the mainloop has exited and can be used for
     cleanup actions. The helper will exit when this method returns.

  The ``handle_options`` method of the ``Ubot::Helper`` class also sets up some
  signal receivers so bot state is updated and messages are listened to. You
  should not override these methods, instead you can provide hooks for them to
  call.

  .. function:: message_sent(self, command, params)
  .. function:: message_received(self, prefix, command, target, params)

     These functions turn their arguments into :class:`Irc::InMessage` or
     :class:`Irc::OutMessage` objects which then are passed to hooks you can
     provide. These hooks should be named ``in_<command>`` or
     ``out_<command>``.

     The ``Ubot::Helper`` class does not provide any such hooks, so you should
     not try to call any superclass hooks.

  .. function:: sync_complete

     Updates ``self.synced`` and initializes the ``channels`` attribute.

  .. function:: master_change

     Updates ``self.am_master``

  The bot also listens to the ``exiting`` signal and will stop the mainloop if
  that signal is received and implements the mandatory ``quit`` and
  ``get_info`` methods. The latter requires you to supply a ``helper_info``
  dictionary as in the example. All keys are mandatory.

  .. function:: addressed(message)

     Call this function in every ``in_<command>`` method to determine whether
     you should act on this message. It will return ``False`` if the bot is not
     synced or not the cluster master. You can override this in your subclass
     if you have your own conditions, but you must always call the parent
     function.

  .. function:: error(message)
  .. function:: warning(message)
  .. function:: info(message)
  .. function:: debug(message)

     These functions log a message via the bot with the apropriate loglevel.

.. class:: Ubot::Responder(Ubot::Helper)

  This class is the one to subclass if you want to respond to incoming
  messages. It inspects one additional configuration key: ``channels``. Its
  value should be a comma-separated list of channels where the bot will
  respond. The words ``all`` and the name of the bot are valid entries too. The
  former will make it respond to all channels. The latter will make it respond
  to private messages.

  .. function:: addressed(message)

     This class' addressed function will return ``true`` only if the channel
     the message was received on is in the list of channels the helper should
     respond to.

  .. function:: send(self, target, message, action, slow)

     This function can be used to send a message. It is rarely used directly,
     but it is used by the :func:`reply` function of the :class:`InMessage`
     class. This also implies that the reply function can only be used only in
     subclasses of ``UbotResponder``.

.. class:: Ubot::Commander(Ubot::Responder)

   A common idiom for helpers is helpers that respond only to certain commands,
   all prefixed with the same character. This helper will read that prefix
   chracter from the configuration (key: prefix) and the addressed function
   will only return ``true`` if the message starts with that prefix
   character.

   .. function:: in_privmsg(self, message)

      This helper also defines an ``in_privmsg()`` method which you can use,
      but don't have to. If you want to override it, you should not call the
      method provided by this class.

      If you want to use this method, you should define a ``commands``
      dictionary that maps commands to the name of a method to call. The called
      method will receive the message with the prefix removed as argument.

The ubot.irc module
-------------------

This module contains various IRC-related utilities and protocol-specific classes.

.. class:: Irc::InMessage

  This class represents an incoming message. Messages have a prefix (the
  nick\!ident@host string for the sender), a command (such as PRIVMSG) and
  parameters. Some messages have a target.

  .. function:: __init__(self, prefix, cmd, params, target)

     Initializer function. All arguments are set as attributes of the resulting
     object.

  .. function:: is_ctcp(self)

     Whether a message is a ctcp message (such as a DCC invitation)

  .. function:: is_action(self)

     Whether a message is an action (Like /me does something)

  .. function:: reply(self, message, action=false, private=false, slow=false)

     Utility function to reply to a message (works only for subclasses of
     :class:`UbotResponder`). 

.. class:: Irc::OutMessage

  This class represents an outgoing message. Messages have a command (such as
  PRIVMSG) and parameters.

  .. function:: __init__(self, command, params)

     Initializer function. All arguments are set as attributes of the resulting
     object.

.. class:: Irc::IrcString

  A subclass of the default unicode object that does all its comparisons not
  only case-insensitive, but the following mapping from rfc 2812 is taken into
  account as well:

  ===== =====
  Lower Upper
  ===== =====
  {     [
  }     ]
  \|    \\
  ^     ~
  ===== =====

  This mapping is used in comparisons and for case-modifying functions.

.. data:: Has_target

   A list of commands that have a target. (channel or nickname)

.. data:: Nargs_in

   A dictionary mapping commands to the number of arguments that don't need to
   be prefixed with a :

.. data:: Nargs_out

   A dictionary mapping commands to the number of arguments that don't need to
   be prefixed with a :

.. data:: Replies

   A dictionary mapping numerical replies to descriptive ones.

.. data:: Channel_user_modes

   A mapping of channel user modes to nickname prefixes (op, voice)

Configuration file
------------------
Each helper must have a configuration file, which must be an ini file. Our
example helper needs nothing more than the following.

.. code-block:: ini

  [hello]
  prefix   = @
  channels = #microbot
  botname  = ubot

The section name must be the same as the name of the bot, given via the ``-n``
commandline argument or taken from the class name as described above. Given
that the helper does not need extra configuration, only the keys defined by the
parent classes are required. There is no limit as to how many sections and keys
you define. All that matters is that it is valid ini syntax.

Service definition
------------------
For D-Bus to be able to autostart your helper, you should also write a service
definition and place it in the service directory (by default
:file:`~/.config/ubot/services/`). For the hello service, this would look like:

.. code-block:: ini

  [D-BUS Service]
  Name=net.seveas.ubot.helper.hello
  Exec=/path/to/helpers/rb_hello -c ~/.config/ubot/hello.conf

Making your helper autostartable is of course not mandatory.
