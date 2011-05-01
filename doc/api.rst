Extending µbot
==============

µbot cannot be extended, but functionality can by providers that live in
different processes and communicate with µbot via D-Bus. The D-Bus API is
documented and there are python, perl and ruby implementations of a heper
library that make it really easy to write new helpers.

For the D-Bus API, the full reference for all interfaces is available.

The python, perl and ruby library all follow the same pattern, so helpers in
either language should look fairly similar. The documentation explains how to
write a helper and the full available API.

.. toctree::

   dbusapi
   python
   perl
   ruby
