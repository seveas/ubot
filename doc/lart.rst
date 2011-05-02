Lart
====

This plugin allows you to lart other people in your channels.

Example
-------
::

  <Seveas> @lart LjL
  * MicroBot replaces Ubuntu with Windows Vista on LjL's PC

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
larts    None    File containing the larts (an example file is shipped with µbot)
channels None    In which channels should the helper respond
======== ======= ================================================================

Commands
--------

* @lart <target>
* @pity <target>
* @slander <target>

Calling either of these commands sends a nastygram to the target to punish him
for doing something stupid. But beware, it can backfire too!
