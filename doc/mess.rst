Random mess
===========

This plugin can give you some random mess to waste time and spam the channel.

Example
-------
::

  <Seveas> @bruce
  <MicroBot>  Bruce Schneier deduced the state of Schrödinger's cat. It is Oklahoma.

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

========= ======= ================================================================
Key       Default Meaning
========= ======= ================================================================
prefix    @       Command prefix character
channels  None    In which channels should the helper respond
offensive None    Channels where some of the more risky commands are allowed
data      None    The directory where datafiles for the commands are stored
========= ======= ================================================================

Commands
--------

================ ===================================================
@t               Random Mr. T. fact from 4q.cc
@chuck           Random Chuck Norris fact from 4q.cc
@vin             Random Vin Diesel fact from 4q.cc
@bauer           Random Jack Bauer fact from notrly.com
@bruce           Random Bruce Schneier fact from geekz.co.uk
@hamster         Bob sez! Or so says hamsterrepublic.com
@bush or @dubya  Random Dubya quote
@mjg or @mjg59   Random Matthew Garrett fact from rjek.com
@vmjg or @vmjg59 Pretend to be Matthew Garrett
@shakespeare     Shakespearesque insults
@bofh            BOFH excuse of the day
@42              HHGTTG quotes
@magic8ball      Get a clear answer to lifes most pressing questions
@ferengi         Ferengi rules of acquisition
@ralph           Ralph
@dice [number]   Roll some dice
@fortune         Virtual fortune cookie
@ofortune        Colorful virtual fortune cookie
@futurama        Futurama quotes from slashdot
@pony            Can I have a pony?
================ ===================================================
