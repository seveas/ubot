Website checker
===============

This plugin will check whether a website is up according to isup.me.

Example
-------
::

  <Seveas> @isup www.ubuntu.com
  <MicroBot> It's just you. http://www.ubuntu.com is up.

Commandline arguments
---------------------
This helper defines the folloing commandline arguments:

============ ============================== ================================
Argument     Default                        Meaning
============ ============================== ================================
-a/--address tcp\:host=localhost,port=11235 Address of the D-Bus session bus
-n/--name    Named after the helper class   D-Bus service name of the helper
-c/--config  No default, mandatory          Configuration file
============ ============================== ================================

Configuration keys
------------------

This helper needs the following keys in its configuration section:

======== ======= ================================================================
Key      Default Meaning
======== ======= ================================================================
prefix   @       Command prefix character
channels None    In which channels should the helper respond
======== ======= ================================================================

Commands
--------

* @isup <hostname>

Checks isup.me to see whether the website is up and responds with the result.
