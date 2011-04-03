import ubot.channel
import ubot.exceptions
import ubot.irc
import ubot.rfc2812

import copy, datetime, dbus, gobject, logging, os, random, re, signal, sys, time
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import cPickle as pickle
DBusGMainLoop(set_as_default=True)

class Ubot(dbus.service.Object):

    # Initialization and data handling functions

    def __init__(self, config):
        self.config = config
        self.ircconnection = None
        dbus.SessionBus().add_signal_receiver(self.helper_exited, signal_name='NameOwnerChanged',
                dbus_interface='org.freedesktop.DBus', bus_name='org.freedesktop.DBus', path='/org/freedesktop/DBus')
        self.busname = dbus.service.BusName("net.seveas.ubot." + config.busname, dbus.SessionBus())
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/net/seveas/ubot/' + config.busname)
        data = {}
        self.ignores = []
        if os.path.exists(self.config.datafile):
            fd = open(self.config.datafile)
            data = pickle.load(fd)
            fd.close()
            fd.close()
        self.saved_channels = data.get('channels',set([]))
        if self.config.controlchan not in self.saved_channels:
            self.saved_channels.add(self.config.controlchan)
        self.tojoin = copy.deepcopy(self.saved_channels)
        self.passwords = data.get('passwords',{})
        self.ignores = data.get('ignores',[])
        self.master = False
        self.clear_data()
        self.helpers = {}
        self.logger = logging.getLogger('ubot')
        self.msglogger = logging.getLogger('ubot.messages')

    def clear_data(self):
        """Clear internal data, used when diconnected"""
        if hasattr(self, 'channels'):
            for c in self.channels.values():
                c.remove_from_connection()
                del(c)
        self.channels = {}
        self.prefixes = {}
        self.nick = ''
        self.connected = False
        self.server = None
        self.port = None
        self.synced = len(self.saved_channels) == 0
        self.tojoin = copy.deepcopy(self.saved_channels)
        self.loggedin = False
        for p in self.config.peers:
            p.is_active = False
        self.master_change(False)
        self.last_recv = time.time()
        self.ping_sent = 0

    def flush(self):
        obj = {
            'channels': self.saved_channels,
            'ignores': self.ignores
        }
        with open(self.config.datafile, 'w') as fd:
            pickle.dump(obj,fd)

    def run(self):
        """Start the bot"""
        self.logger.info("Connecting to %s" % str(self.config.servers))
        self.ircconnection = ubot.irc.IrcConnection(self.config.servers, self)
        if not self.ircconnection.socket:
            self.logger.error("Unable to connect")
            return
        gobject.timeout_add(60000, self.clean_prefixes)
        gobject.timeout_add(60000, self.ping)
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def clean_prefixes(self):
        """Clean old prefixes from the cache"""
        cutoff = time.time() - 900
        for p in self.prefixes.keys():
            if self.prefixes[p][1] + 900 < cutoff:
                self.prefixes.pop(p)
        return True

    def isme(self, msg):
        """Determine if a message/prefix/nick is the bot's"""
        if isinstance(msg, ubot.irc.InMessage):
            return msg.nick == self.nick
        elif '!' in msg:
            return msg[:msg.index('!')] == self.nick
        return msg == self.nick

    def helper_exited(self, name, old, new):
        if name in self.helpers and new == '':
            self.helpers.pop(name)

    # Generic connectivity funcions

    def ping(self):
        """Ping the server and disconnect if it doesn't reply"""
        now = time.time()
        if now - self.last_recv > 60 and self.ping_sent:
            self.logger.error("No message in %d seconds, disconnecting" % (now-self.last_recv))
            self.ircconnection.reconnect()
        elif now - self.last_recv > 60:
            self.logger.info("No message in %d seconds, sending ping" % (now - self.last_recv))
            self.ircconnection.send(ubot.irc.OutMessage('PING', ['am_i_still_connected']))
            self.ping_sent = now
        return True

    def login(self):
        """Identify to the server"""
        self.nick = self.config.nicks[0]
        self.logger.info("Logging in as %s" % self.nick)
        if self.config.password:
            self.ircconnection.send(ubot.irc.OutMessage('PASS', [self.config.password]))
        self.ircconnection.send(ubot.irc.OutMessage('USER', [self.config.ident, '12', '*', self.config.realname]))
        self.ircconnection.send(ubot.irc.OutMessage('NICK', [self.config.nicks[0]]))
        self.loggedin = 1

    def handle_message(self, message):
        """Handle an incoming/outgoing message"""
        # Log the message
        self.msglogger.info(repr(message))
        if self.verbose:
            print "%s %s" % (datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), repr(message))
            if self.verbose > 1 and message.raw:
                print ' ' * 17 + message.raw.strip()

        # Shortcut the short case, sent messages
        if isinstance(message, ubot.irc.OutMessage):
            self.message_sent(message.command, message.params)
            return

        self.last_recv = time.time()
        # Should we ignore this message?
        if message.command in ('PRIVMSG', 'NOTICE') and not self.isme(message):
            for i in self.ignores:
                if i.match(message.prefix):
                    return

        # Send dbus signal
        self.message_received(message.prefix or '', message.command, message.target or '', message.params)

        # Handle the message internally
        if message.prefix and message.nick:
            self.prefixes[message.nick] = (message.prefix,time.time())
        if not self.loggedin:
            self.login()
        handlers = ['handle_%s' % message.command.lower()]
        if message.ncommand and message.ncommand in ubot.irc.replies:
            handlers += ['handle_%s' % ubot.irc.replies[message.ncommand][4:].lower()]
        for h in handlers:
            if hasattr(self, h):
                getattr(self, h)(message)
                break

        # Are we synced yet
        if not self.synced and message.command in ('RPL_ENDOFNAMES', 'ERR_BANNEDFROMCHAN', 'ERR_INVITEONLYCHAN',
                                                   'ERR_CHANNELISFULL', 'ERR_NOSUCHCHANNEL', 'ERR_TOOMANYCHANNELS',
                                                   'ERR_BADCHANNELKEY', 'ERR_BADCHANMASK'):
            if message.params[0] in self.tojoin:
                self.tojoin.remove(message.params[0])
            if len(self.tojoin) == 0:
                self.sync_complete()

    # Dbus signals and methods

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='sssas')
    def message_received(self, prefix, command, target, params):
        """Send the received message over the dbus"""
        pass

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='sas')
    def message_sent(self, command, params):
        """Send the sent message over the dbus"""
        pass

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='')
    def exiting(self):
        """We are on our way out"""
        pass

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='')
    def sync_complete(self):
        """We have synced"""
        self.synced = True
        self.logger.info("Channel synchronization complete")
        if self.config.controlchan in self.channels:
            self.channels[self.config.controlchan].say(random.choice(FAILOVER_HELLO))
            self.maybe_master()

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='b')
    def master_change(self, value):
        if self.master == value:
            return
        if value:
            self.logger.info("Assuming master role")
        else:
            self.logger.info("Dropping master role")
        self.master = value

    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='')
    def connection_dropped(self):
        self.clear_data()
    
    @dbus.service.signal(dbus_interface='net.seveas.ubot', signature='si')
    def connection_made(self, server, port):
        self.server = server
        self.port = port
        self.connected = True

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='so', out_signature='')
    def register_helper(self, service, path):
        self.helpers[service] = path

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='', out_signature='aas')
    def get_helpers(self):
        return self.helpers.items()

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='', out_signature='as')
    def get_channels(self):
        """Return a list of channels"""
        return self.channels.keys()

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='', out_signature='a{sv}')
    def get_info(self):
        return {
            'version': ubot.version,
            'synced': self.synced,
            'master': self.master,
            'nickname': self.nick,
            'connected': self.connected,
            'server': self.server,
            'port': self.port,
        }

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='ss', out_signature='')
    def join(self, channel, password=''):
        """Join a channel, optionally with password"""
        if password:
            self.passwords[channel] = password
            self.ircconnection.slowsend(ubot.irc.OutMessage('JOIN', [channel, password]))
        else:
            self.ircconnection.slowsend(ubot.irc.OutMessage('JOIN', [channel]))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='s', out_signature='')
    def quit(self, quitmessage):
        """Quit from the server"""
        self.exiting()
        self.ircconnection.exiting = True
        self.ircconnection.fastsend(ubot.irc.OutMessage('QUIT', [quitmessage]))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='ss', out_signature='')
    def say(self, user, message):
        """Send a message to a user"""
        if len(user) < 1 or user[0] in '#@%':
            raise ubot.exceptions.InvalidTargetException('Can only send to people')
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [user, message]))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='ss', out_signature='')
    def do(self, user, message):
        """Send a message to a user"""
        if len(user) < 1 or user[0] in '#@%':
            raise ubot.exceptions.InvalidTargetException('Can only send to people')
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [user, '\x01ACTION ' + message + '\x01']))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='ss', out_signature='')
    def slowsay(self, user, message):
        """Send a message to a user"""
        if len(user) < 1 or user[0] in '#@%':
            raise ubot.exceptions.InvalidTargetException('Can only send to people')
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [user, message]))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='ss', out_signature='')
    def slowdo(self, user, message):
        """Send a message to a user"""
        if len(user) < 1 or user[0] in '#@%':
            raise ubot.exceptions.InvalidTargetException('Can only send to people')
        self.ircconnection.send(ubot.irc.OutMessage('PRIVMSG', [user, '\x01ACTION ' + message + '\x01']))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='s', out_signature='')
    def nick(self, newnick):
        self.ircconnection.send(ubot.irc.OutMessage('NICK',[newnick]))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='sss', out_signature='', sender_keyword='sender')
    def log(self, ident, level, msg, sender=None):
        if level not in logging._levelNames.values():
            return
        logging.getLogger('ubot.helper.' + ident).log(getattr(logging,level), u'(%s) %s' % (sender, msg))
    
    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='sas', out_signature='')
    def rawmsg(self, cmd, args):
        """Send a raw message to the server"""
        self.ircconnection.send(ubot.irc.OutMessage(cmd, args))

    @dbus.service.method(dbus_interface='net.seveas.ubot',
                         in_signature='s', out_signature='as')
    def list_channels(self, nick):
        nick = ubot.rfc2812.IrcString(nick)
        return [x.name for x in self.channels.values() if nick in x.nicks]

    # Message handlers

    def handle_welcome(self, msg):
        self.nick = msg.target
        self.loggedin = 2
        for c in self.saved_channels:
            self.join(c, self.passwords.get(c,''))
    
    # Ping-pong with the server
    def handle_ping(self, msg):
        self.ircconnection.fastsend(ubot.irc.OutMessage('PONG', msg.params))
    
    def handle_pong(self, msg):
        if msg.params[1] == 'am_i_still_connected':
            self.ping_sent = 0
        if msg.params[1] == '1':
            self.ircconnection.ponged()
    
    # Channel administration
    def handle_join(self, msg):
        if self.isme(msg):
            self.logger.info("Joined channel %s" % msg.target)
            self.saved_channels.add(msg.target)
            self.flush()
            self.channels[msg.target] = ubot.channel.Channel(self, msg.target)
            self.ircconnection.slowsend(ubot.irc.OutMessage('MODE', [msg.target]))
        else:
            self.channels[msg.target].nicks.append(msg.nick)
        for p in self.config.peers:
            if p.isme(msg):
                self.channels[msg.target].say(random.choice(FAILOVER_HELLO))
    
    def handle_part(self, msg):
        if self.config.controlchan == msg.target:
            if self.isme(msg):
                self.master_change(False)
            else:
                for p in self.config.peers:
                    if p.isme(msg):
                        p.is_active = False
                        self.maybe_master()
        if not self.isme(msg):
            self.channels[msg.target].nicks.remove(msg.nick)
            return
        self.logger.info("Left channel %s" % msg.target)
        c = self.channels.pop(msg.target)
        c.remove_from_connection() # dbus connection, that is
        del(c)
    
    def handle_kick(self, msg):
        nick = msg.params[0]
        if self.config.controlchan == msg.target:
            if self.isme(msg.params[0]):
                return self.master_change(False)
            for p in self.config.peers:
                if p.isme(msg.params[0]):
                    p.is_active = False
                    self.maybe_master()
        if not self.isme(nick):
            self.channels[msg.target].nicks.remove(nick)
            return
        self.logger.info("Was kicked from channel %s by %s" % (msg.target, msg.nick))
        c = self.channels.pop(msg.target)
        c.remove_from_connection()
        del(c)
        self.join(msg.target)
    
    def handle_namreply(self, msg):
        cname, nicks = msg.params[-2:]
        self.channels[cname].nicks += [_nomode(x) for x in nicks.split()]
    
    def handle_endofnames(self, msg):
        cname = msg.params[0]
        self.channels[cname].synced = True
        if cname == self.config.controlchan and self.synced:
            # We've returned after kick/part or joined for the first time
            self.channels[msg.params[0]].say(random.choice(FAILOVER_HELLO))
            self.maybe_master()
    
    def handle_privmsg(self, msg):
        if msg.target == self.config.controlchan:
            for p in self.config.peers:
                if p.isme(msg) and msg.params[0] in FAILOVER_HELLO:
                    p.is_active = True
                    self.maybe_master()
    
    def handle_nick(self, msg):
        if self.isme(msg):
            self.nick = msg.params[0]
        for c in self.channels.values():
            if msg.nick in c.nicks:
                c.nicks.remove(msg.nick)
                c.nicks.append(msg.params[0])
    
    def handle_quit(self, msg):
        if msg.target == self.config.controlchan:
            for p in self.config.peers:
                if p.isme(msg):
                    p.is_active = False
                    self.maybe_master()
        for c in self.channels.values():
            if msg.nick in c.nicks:
                c.nicks.remove(msg.nick)
    
    def handle_nicknameinuse(self, msg):
        # Only time we should act on this is when self.loggedin = 1 (tried login, not seen welcome)
        if self.loggedin == 1:
            pos = self.config.nicks.index(msg.params[0])
            if pos == len(self.config.nicks) -1:
                self.logger.error("Exhausted all nicknames")
                self.mainloop.quit()
            self.ircconnection.send(ubot.irc.OutMessage('NICK', [self.config.nicks[pos+1]]))
    
    def handle_topic(self, msg):
        self.channels[msg.params[0]].topic = msg.params[1]
    
    def handle_channelmodeis(self, msg):
        self.channels[msg.params[0]].mode = msg.params[1:]

    def handle_mode(self, msg):
        # Be lazy, don't manage modes but re-request them
        if msg.params[0] in self.channels:
            self.rawmsg('MODE', [msg.params[0]])

    def maybe_master(self):
        # Not synced, not master
        if not self.synced:
            return self.master_change(False)
        # Am I the highest priority active bot
        minpri = self.config.priority
        for p in self.config.peers:
            if p.is_active:
                minpri = min(p.priority, minpri)
        if minpri == self.config.priority:
            self.master_change(True)
        else:
            self.master_change(False)

# Many thanks to Douglas Adams for writing the hitchhikers guide
FAILOVER_HELLO = ("Ah, hello, Number Two",
                  "Ford! Hello, how are you?",
                  "Hi, Have you got a drink?",
                  "Bet you weren't expecting to see me again",
                  "Have you come far?",
                  "What...? Who...? When...? Where...?",
                  "Welcome to the starship heart of gold")

def _nomode(x):
    while x[0] in '@%+~':
        x = x[1:]
    return x
