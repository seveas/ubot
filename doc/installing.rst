Installing µbot
===============

Prerequisites
-------------
µbot works best on a modern linux distribution, such as recent versions of
Ubuntu or Fedora The following packages are required:

* Python 2.5 or newer
* DBus
* Perl 5.10.1 or newer
* Ruby 1.8 or newer
* D-Bus bindings for all these languages
* Django
* Git, if you want to run from source

Some extra libraries are needed too:

* Config::Ini (perl)
* Nokogiri (ruby)
* pygobject (part of pygtk) (python)
* icalendar (python)

Mysql or postgres may be used for database support instead of the default
sqlite database.

To install all these on Ubuntu, you can enter the following command: ::

 sudo apt-get install python dbus python-dbus python-django libnet-dbus-perl \
                      libconfig-ini-perl ruby-nokogiri ruby-dbus \
                      python-gobject mysql-server-5.1 python-mysqldb git

Installing µbot
---------------
Currently µbot is only available by cloning from github_. Open a terminal and
go to wherever you want to download the code. Then enter the following command
to download µbot: ::

  git clone git://github.com/seveas/ubot.git

This will create a directory named :file:`ubot`. Enter that directory to
install ubot. Run the following commands to install into your home directory: ::

  ./autogen.sh --prefix=$HOME/ubot_inst
  make
  make install

After the first command, you will see some advise about your :file:`~/.bashrc`.
Please follow that advise.

You can now :doc:`run ubot <running>`. The first time you run it, it will prompt you for some
basic configuration and it will create all needed config and data files in
:file:`~/.config/ubot` and :file:`~/.local/share/ubot`.

.. _github: https://github.com/seveas/ubot
