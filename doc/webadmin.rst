The µbot web interface
======================

The µbot web interface is a django application that can integrate with an
existing django environment. For your convenience, a complete django project is
shipped with µbot as well, this lives in the :file:`botweb` directory.

Configuring django
------------------
To use the shipped web environment, copy the botweb directory somewhere. Then
edit the file :file:`settings.py` to reflect your environment. Usually all you
need to change is the `ADMINS` setting and the default password.

If you want to integrate µbot in your existing django project, you need to do
the following: 

* Add `ubot.control` to your `INSTALLED_APPS`
* Set `UBOT_BOTNAME`
* Set `DBUS_SESSION_BUS_ADDRESS` to the address configured in the D-Bus
  configuration
* Add a line to your patterns in the your `ROOT_URLCONF` like this:
  `(r'^control/', include('ubot.web.control.urls')),`

Configuring your webserver
--------------------------
To start the built-in django webserver, all you need to do is run `./manage.py
runserver` from your copy of the botweb directory. However, it is recommended
that you use a real webserver instead. For information on configuring a
webserver for django, please follow the `Django documentation`_.

.. _`Django documentation`: http://docs.djangoproject.com

Initializing a django project
-----------------------------
Whether you are creating a new django project or adding µbot to your existing
one, you shoudl run `./manage.py syncdb` before trying to use the web
interface.

Using the web interface
-----------------------
To control the bot, go to your website (if you run the simple django server:
http://127.0.0.1:8000/control/). If the bot is not yet running, you can start
it there. You can also join/part channels, stop the bot, control helpers and do
some more administrative actions.

Only django superusers currently can use the web interface.
