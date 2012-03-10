import ubot.irc
import ubot.util
import dbus, dbus.service

class Channel(dbus.service.Object):
    def __init__(self, bot, name):
        self.name = name
        self.synced = False
        self.nicks = {}
        self.config = bot.config
        self.ircconnection = bot.ircconnection
        self.bot = bot
        self.topic = ''
        self.mode = []
        self.limit = 0
        self.key = ''
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/net/seveas/ubot/%s/channel/%s' % 
                                     (self.config.busname, ubot.util.escape_object_path(self.name)))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def part(self, partmsg=''):
        self.bot.saved_channels.remove(self.name)
        self.bot.flush()
        self.ircconnection.send(ubot.irc.OutMessage('PART', [self.name, partmsg]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def say(self, msg):
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [self.name, msg]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def do(self, msg):
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [self.name, '\01ACTION ' + msg + '\01']))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def slowsay(self, msg):
        self.ircconnection.slowsend(ubot.irc.OutMessage('PRIVMSG', [self.name, msg]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def slowdo(self, msg):
        self.ircconnection.slowsend(ubot.irc.OutMessage('PRIVMSG', [self.name, '\01ACTION ' + msg + '\01']))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='ss', out_signature='')
    def kick(self, who, msg):
        self.ircconnection.send(ubot.irc.OutMessage('KICK', [self.name, who, msg]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def invite(self, nick):
        self.ircconnection.send(ubot.irc.OutMessage('INVITE', [nick, self.name]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='as', out_signature='')
    def set_mode(self, modeargs):
        modeargs = [str(x) for x in modeargs]
        print "XXX", modeargs
        self.ircconnection.send(ubot.irc.OutMessage('MODE', [self.name] +modeargs))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='', out_signature='as')
    def get_mode(self):
        return self.mode

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='', out_signature='s')
    def get_topic(self):
        return self.topic

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='s', out_signature='')
    def set_topic(self, topic):
        self.ircconnection.slowsend(ubot.irc.OutMessage('TOPIC', [self.name, topic]))

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='', out_signature='a{ss}')
    def get_nicks(self):
        return self.nicks

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='', out_signature='s')
    def get_key(self):
        return self.key

    @dbus.service.method(dbus_interface='net.seveas.ubot.channel',
                         in_signature='', out_signature='i')
    def get_limit(self):
        return self.limit
