Root warner
===========

This plugin will send a private warning to anybody who joins your channil with
root as nickname or ident.

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

======== ======= =================================================
Key      Default Meaning
======== ======= =================================================
channels None    In which channels should display alerts
======== ======= =================================================
