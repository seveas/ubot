import ConfigParser, dbus, gobject, optparse, os, re, sys
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import ubot.exceptions
import ubot.util
from ubot.irc import InMessage, OutMessage, IrcString

class UbotHelper(dbus.service.Object):
    def add_options(self, parser):
        parser.add_option('-a', '--address', dest='address', default='tcp:host=localhost,port=11235',
                          help='The address of your session bus', metavar='ADDRESS')
        parser.add_option('-n', '--name', dest='name', help='Plugin name', metavar='NAME')
        parser.add_option('-c', '--config', dest='config', default=None, help='Specify configfile', metavar='FILE')

    def handle_options(self, opts, args):
        if opts.name:
            self.name = opts.name
        else:
            self.name = self.__class__.__name__.lower()
            self.name = re.sub('(help|respond|command|notifi|listen)er', '', self.name)

        self.conf = None
        if opts.config:
            opts.config = os.path.expanduser(opts.config)
            if os.path.exists(opts.config):
                defaults = {'botname': 'ubot', 'prefix': '@', 'busname': self.name}
                self.conf = ConfigParser.ConfigParser(defaults)
                self.conf.read(opts.config)
            else:
                raise ubot.exceptions.ConfigError('No such configfile')
        else:
            raise ubot.exceptions.ConfigError('No configfile specified')

        self.busname = self.conf.get(self.name, 'busname')
        if '.' not in self.busname:
            self.busname = 'net.seveas.ubot.helper.' + self.busname
        self.busobjname = '/' + self.busname.replace('.', '/')
        self.busnameobj = dbus.service.BusName(self.busname, dbus.SessionBus())
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.busobjname)

        self.botname = self.conf.get(self.name, 'botname')
        self.get_bot()

        # Detect bot exits and reconnects
        dbus.SessionBus().add_signal_receiver(lambda x, y, z: self.get_bot(),
                                              signal_name='NameOwnerChanged', dbus_interface='org.freedesktop.DBus',
                                              bus_name='org.freedesktop.DBus', path='/org/freedesktop/DBus',
                                              arg0=u'net.seveas.ubot.' + self.botname)

    def get_bot(self):
        self.bot = dbus.SessionBus().get_object('net.seveas.ubot.' + self.botname,
                                                '/net/seveas/ubot/' + self.botname)
        self.bot.register_helper(self.busname, self.busobjname)
        self.bot.connect_to_signal('message_sent', self.message_sent, dbus_interface='net.seveas.ubot.bot')
        self.bot.connect_to_signal('message_received', self.message_received, dbus_interface='net.seveas.ubot.bot')
        self.bot.connect_to_signal('sync_complete', self.sync_complete, dbus_interface='net.seveas.ubot.bot')
        self.bot.connect_to_signal('master_change', self.master_change, dbus_interface='net.seveas.ubot.bot')
        self.bot.connect_to_signal('exiting', lambda: self.mainloop.quit(), dbus_interface='net.seveas.ubot.bot')
        info = self.bot.get_info()
        self.bot_version, self.master, self.synced, self.nickname = info['version'], info['master'], info['synced'], info['nickname']
        self.channels = {}
        if self.synced:
            self.sync_complete()
        self.nickname = IrcString(self.nickname)

    # Handle bus messages
    def message_sent(self, command, params):
        message = OutMessage(command, params)
        if hasattr(self, 'out_' + command.lower()):
            getattr(self, 'out_' + command.lower())(message)

    def message_received(self, prefix, command, target, params):
        message = InMessage(IrcString(prefix), IrcString(command), [IrcString(x) for x in params], IrcString(target))
        message.helper = self
        command = command.replace('CMD_','').replace('RPL_','').lower()
        if hasattr(self, '_in_' + command.lower()):
           getattr(self, '_in_' + command.lower())(message)
        if hasattr(self, 'in_' + command.lower()):
           getattr(self, 'in_' + command.lower())(message)

    def sync_complete(self):
        # Request list of channels
        self.synced = True
        self.channels = dict([(x, dbus.SessionBus().get_object('net.seveas.ubot.' + self.botname, 
                               '/net/seveas/ubot/%s/channel/%s' % (self.botname, ubot.util.escape_object_path(x))))
                              for x in self.bot.get_channels()])

    def master_change(self, am_master):
        self.master = am_master

    def _in_part(self, message):
        if message.prefix.startswith(self.nickname + '!'):
            x = self.channels.pop(message.target)
            del(x)

    def _in_join(self, message):
        if message.prefix.startswith(self.nickname + '!'):
            self.channels[message.target] = dbus.SessionBus().get_object('net.seveas.ubot.' + self.botname, 
                '/net/seveas/ubot/%s/channel/%s' % (self.botname, ubot.util.escape_object_path(message.target)))

    def _in_nick(self, message):
        if message.prefix.startswith(self.nickname + '!'):
            self.nickname = message.params[0]

    def addressed(self, message):
        return self.synced and self.master

    def error(self, msg):
        self.bot.log(self.name, 'ERROR', msg)

    def warning(self, msg):
        self.bot.log(self.name, 'WARNING', msg)

    def info(self, msg):
        self.bot.log(self.name, 'INFO', msg)

    def debug(self, msg):
        self.bot.log(self.name, 'DEBUG', msg)

    @classmethod
    def run(klass):
        c = klass()
        c.name = klass.__name__
        parser = optparse.OptionParser()
        c.add_options(parser)
        
        opts, args = parser.parse_args()
        os.environ['DBUS_SESSION_BUS_ADDRESS'] = os.environ.get('DBUS_STARTER_ADDRESS', opts.address)

        c.handle_options(opts, args)
        c.info("helper started")
        c.mainloop = gobject.MainLoop()
        c.mainloop.run()
        c.exit()

    def exit(self):
        # Empty method, provided for consistency, so you can call super() for it.
        pass

    @dbus.service.method(dbus_interface='net.seveas.ubot.helper',
                         in_signature='', out_signature='')
    def quit(self):
        self.mainloop.quit()

    @dbus.service.method(dbus_interface='net.seveas.ubot.helper',
                         in_signature='', out_signature='a{ss}')
    def get_info(self):
        return self.helper_info

    def get_user(self, prefix):
        return dbus.SessionBus().get_object('net.seveas.ubot.helper.users',
                '/net/seveas/ubot/helper/users').get_user(prefix)

    def register_permission(self, name, description):
        return dbus.SessionBus().get_object('net.seveas.ubot.helper.users',
                '/net/seveas/ubot/helper/users').register_permission(name, description)

class UbotResponder(UbotHelper):
    def handle_options(self, opts, args):
        super(UbotResponder, self).handle_options(opts, args)
        self.active_channels = self.conf.get(self.name, 'channels', '').split(',')
        self.respond_to_all = 'all' in self.active_channels
        self.respond_to_private = self.botname in self.active_channels

    def addressed(self, message):
        if not super(UbotResponder, self).addressed(message):
            return False
        if message.target == self.nickname:
            return self.respond_to_private
        else:
            return self.respond_to_all or (message.target in self.active_channels)

    def send(self, target, message, action=False, slow=False):
        if target.startswith('#'):
            if action:
                if slow:
                    self.channels[target].slowdo(message)
                else:
                    self.channels[target].do(message)
            else:
                if slow:
                    self.channels[target].slowsay(message)
                else:
                    self.channels[target].say(message)
        else:
            if action:
                if slow:
                    self.bot.slowdo(target, message)
                else:
                    self.bot.do(target, message)
            else:
                if slow:
                    self.bot.slowsay(target, message)
                else:
                    self.bot.say(target, message)

class UbotCommander(UbotResponder):
    def handle_options(self, opts, args):
        super(UbotCommander, self).handle_options(opts, args)
        self.prefix = self.conf.get(self.name, 'prefix', '@')

    def addressed(self, message):
        if not super(UbotCommander, self).addressed(message):
            return False
        msg = message.params[0].lstrip()
        for p in self.prefix:
            if msg.startswith(p):
                msg = msg[1:].lstrip()
                break
        else:
            match = re.match(r'^%s[^w](.*)' % self.nickname, msg, flags=re.I)
            if match:
                msg = match.group(1).lstrip()
            else:
                if message.target != self.nickname:
                    return False

        message.params[0] = msg

        # So, prefix was seen
        # Now for the commands
        if hasattr(self, 'commands'):
            _ = msg.split(None, 1)
            if len(_) == 2:
                command, arg = _
            else:
                command, arg = _[0], ''
            if command in self.commands:
                message._command = (command, arg)
                self.info("%s was called in %s by %s with argument %s" % (command, message.target, message.prefix, arg))
                return True
            else:
                return False

        # If a plugin doesn't define a command list, assume it'll do
        # its own argument handling
        return True

    def in_privmsg(self, message):
        if self.addressed(message):
            command, arg = message._command
            getattr(self, command)(message, arg)

class DjangoHelper(object):
    def handle_options(self, opts, args):
        super(DjangoHelper, self).handle_options(opts, args)
        info = self.bot.get_info()
        os.environ['UBOT_DATADIR'] = info['datadir']
        os.environ['DJANGO_SETTINGS_MODULE'] = info['django_settings_module']
