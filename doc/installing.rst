Installing µbot
===============

.. warning::
  As µbot is currently alpha software, there is no installer yet, you can only
  run it from a copy of the source tree.

Prerequisites
-------------
µbot works best on a modern linux distribution, such as Ubuntu 10.10 or Fedora
14. The following packages are required:

* Python 2.5 or newer
* DBus and the python dbus bindings
* Perl DBus bindings (Net::DBus) for the perl example helper
* The django web framework
* pygobject (part of pygtk)
* git

Mysql or postgres may be used for database support instead of the default
sqlite database.

To install all these on Ubuntu, you can enter the following command: ::

 sudo apt-get install python dbus python-dbus python-django libnet-dbus-perl \
                      python-gobject mysql-server-5.1 python-mysqldb git

Downloading µbot
----------------
Currently µbot is only available by cloning from github_. Open a terminal and
go to wherever you want to download the code. Then enter the following command
to download µbot: ::

  git clone git://github.com/seveas/ubot.git

This will create a directory named :file:`ubot`. Go into that directory and run
the code from there.

.. _github: https://github.com/seveas/ubot

Initial configuration
---------------------

When running from source, you can install a copy of the basic configuration
with the :command:`bin/run_from_source.sh` command. This will copy basic
configuration files into :file:`~/.config/ubot` and some data files into
:file:`~/.local/share/ubot`. When you've done that, you can :doc:`configure
<configuring>` and :doc:`run <running>` the bot!
