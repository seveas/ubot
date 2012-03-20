This is the µbot IRC bot
========================

µbot (aka Microbot), is a very small IRC bot that is designed to be scalable,
fault-tolerant, robust, easy to extend and multilingual.

While µbot itself is tiny, it takes a unique approach to extending: where
traditionally added functionality is written as plugins, or dynamically loaded
modules, µbot's helpers all run in separate processes.

These processes communicate with the bot via D-Bus and can thus be managed
completely separately. This decoupling, and the libraries shipped with µbot
make it very easy to add functionality. You can even write helpers in
completely different language, as long as there are D-Bus bindings!

µbot is also easy to manage, the configuration is done in simple .ini files and
there is a web admin with which you can control the bot and its helpers.

Table of contents
-----------------

.. toctree::
   :maxdepth: 1

   installing
   configuring
   running
   helpers
   api
   contributing
   copying
