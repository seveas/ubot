Welcome to the µbot IRC bot's documentation!
============================================

µbot is a very small IRC bot that is designed to be scalable, fault-tolerant,
robust and multilingual.

µbot itself is tiny, the bot has only a few core tasks and not many will be
added in the future. The tasks it has:

* Connect to IRC and be responsible for sending and receiving message
* Internal channel administration
* Failover management
* Broadcasting sent and received messages to helpers

All other functionality is provided by helper programs that live in separate
processes and thus cannot destroy µbots internal state, and they can be stopped
and started separately. They can even be written in different languages!

.. toctree::
   :maxdepth: 2

   installing
   configuring
   running
   webadmin
   helpers
   api
   contributing
   copying
