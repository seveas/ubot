from ubot.rfc2812 import has_target, nargs_out, nargs_in, replies, IrcString
import chardet, gobject, logging, signal, socket, string, sys, time

def try_connect(servers):
    logger = logging.getLogger('ubot.irc')
    for server in servers:
        if ':' in server:
            server, port = server.split(':')
            try:
                port = int(port)
            except:
                pass
        else:
            server, port = server, 6667
        logger.info("Trying to connect to %s port %d" % (server, port))
        try:
            family, socktype, proto, canonname, sockaddr = socket.getaddrinfo(server, port, socket.AF_INET, socket.SOCK_STREAM)[0]
        except socket.gaierror, e:
            logger.error("Failed (%d) %s" % (e[0], e[1]))
            continue
        try:
            sock = socket.socket(family, socktype, proto)
            sock.settimeout(10)
            sock.connect(sockaddr)
            sock.settimeout(None)
            return sock, server, port
        except socket.error, e:
            logger.error("Failed: (%d) %s" % (e[0], e[1]))
    return (None, None, None)

class IrcConnection(object):
    def __init__(self, servers, bot):
        self.servers = servers
        self.bot = bot
        self.message_handler = bot.handle_message
        self.data = ''
        self.queue = []
        self.slowqueue = []
        self.times = [0,0,0,0,0,0]
        self.quota = 1450 # Allow some room for ping
        self.pinging = False
        self.logger = logging.getLogger('ubot.irc')
        self.exiting = False
        self.socket = None

        gobject.timeout_add(1000, self.handle_queue)
        self.reconnect()

    def ponged(self):
        self.quota = 1500
        self.pinging = False
        self.handle_queue()

    def incoming(self, socket, condition):
        if socket != self.socket:
            # This happens if reconnect is called from outside this function
            # (e.g. by the ping timeout handler) Let's get rid of this watch.
            return False
        if condition & ( gobject.IO_ERR | gobject.IO_HUP):
            self.reconnect()
            # We don't want this particular watch anymore, only the new one
            return False
        _data = self.socket.recv(1024)
        if not _data:
            self.reconnect()
            # We don't want this particular watch anymore, only the new one
            return False
        self.data += _data
        while True:
            i = self.data.find('\r\n')
            if i == -1:
                break
            msg = InMessage.from_string(self.data[:i])
            self.data = self.data[i+2:]
            if msg:
                self.message_handler(msg)
        return True

    def reconnect(self):
        if self.socket:
            self.logger.error("Connection error, reconnecting")
            self.socket = None
            self.bot.connection_dropped()
            if self.exiting:
                self.logger.info("Disconnected, exiting")
                self.bot.mainloop.quit()
        self.data = ''
        self.times = [0,0,0,0,0,0]
        self.queue = []
        self.slowqueue = []
        while True:
            self.socket, server, port = try_connect(self.servers)
            if self.socket:
                self.bot.connection_made(server, port)
                gobject.io_add_watch(self.socket,
                                     gobject.IO_IN | gobject.IO_PRI | gobject.IO_ERR | gobject.IO_HUP,
                                     self.incoming)
                break
            self.logger.error("Couldn't connect to any server, waiting 60 seconds")
            gobject.timeout_add(60000, self.reconnect)
            # Return false here to cancel previous timeout_add
            return False

    def _send(self, msg):
        # FIXME fail on too long messages, or maybe split?
        self.times.pop(0)
        self.times.append(time.time())
        self.quota -= len(msg)
        self.message_handler(msg)
        self.socket.send(unicode(msg).encode('utf-8'))

    def ping(self):
        if not self.pinging:
            self.pinging = True
            msg = OutMessage('PING', ['1'])
            self.message_handler(msg)
            self.socket.send(unicode(msg))

    def send(self, msg):
        if len(msg) > self.quota:
            self.ping()
            self.queue.append(msg)
        else:
            now = time.time()
            #if self.times[-1] + 1 < now and self.times[0] +18 < now:
            if self.times[-1] + 1 < now and self.times[0] +12 < now:
                self._send(msg)
            else:
                self.queue.append(msg)
    
    def fastsend(self, msg):
        if len(msg) > self.quota:
            self.ping()
            self.queue.insert(0,msg)
        else:
            self._send(msg)

    def slowsend(self, msg):
        self.slowqueue.append(msg)

    def handle_queue(self):
        if not self.socket:
            return True
        now = time.time()
        if self.times[-1] + 1 > now or self.times[0] + 18 > now:
            return True
        if self.queue:
            if len(self.queue[0]) > self.quota:
                self.ping()
            else:
                self._send(self.queue.pop(0))
        elif self.slowqueue:
            if len(self.slowqueue[0]) > self.quota:
                self.ping()
            else:
                self._send(self.slowqueue.pop(0))
        return True

class InMessage(object):
    def __init__(self, prefix, cmd, params, target=None):
        self.prefix   = prefix
        self.command  = cmd
        self.ncommand = None
        self.params   = params
        self.nick     = None
        self.host     = None
        self.target   = target
        self.raw      = None

        if '!' in self.prefix and '@' in self.prefix:
            self.nick, self.host = self.prefix.split('@')
            self.nick, self.ident = self.nick.split('!')

        if self.command in replies:
            self.ncommand = self.command
            self.command = replies[self.command]

        if self.command.startswith('RPL_') or self.command.startswith('ERR_') or self.command in has_target:
            if not target:
                self.target = self.params.pop(0)

    @staticmethod
    def from_string(data):
        raw = data
        try:
            data = IrcString(unicode(data, 'utf-8'))
        except:
            try:
                data = IrcString(unicode(data, chardet.detect(data)['encoding']))
            except LookupError:
                data = IrcString(unicode(data, errors='replace'))
            except:
                self.logger.error("Undecodable message received")
                return
        prefix = ''

        if data[0] == ':':
            prefix, data = data[1:].split(None, 1)

        command, data = data.split(None, 1)

        _command = replies.get(command,command)
        if _command in nargs_in:
            if _command.startswith('RPL_') or _command.startswith('ERR_'):
                params = data.split(None, nargs_in[_command] + 1)
            else:
                params = data.split(None, nargs_in[_command])
            if len(params) > nargs_in[_command]:
                params = params[:-1] + [params[-1][1:]]
        else:
            params = data.split()

        if params[0].startswith(':'):
            params[0] = params[0][1:]
        msg = InMessage(prefix, command, params)
        msg.raw = raw
        return msg

    def is_ctcp(self):
        return self.command == 'PRIVMSG' and self.params[-1][0] == self.params[-1][-1] == '\x01'

    def is_action(self):
        return self.is_ctcp() and self.params[-1][1:8] == 'ACTION'

    # used only in helpers
    def reply(self, message, action=False, private=False, slow=False):
        target = self.target
        if private:
            target = self.nick
        self.helper.send(target, message, action, slow)

    def __repr__(self):
        return '<InMessage prefix=%s cmd=%s target=%s params=%s>' % (repr(self.prefix), repr(self.command), repr(self.target), repr(self.params)) 

class OutMessage(object):
    def __init__(self, command, params):
        self.command = IrcString(command)
        self.params = [IrcString(x) for x in params]
        self.prefix = u''

    def __len__(self):
        return len(unicode(self).encode('utf-8'))

    def __unicode__(self):
        if self.command not in nargs_out:
            return "%s %s\r\n" % (self.command, ' '.join(self.params))
        a1 = ' '.join(self.params[:nargs_out[self.command]])
        a2 = ':'+' '.join(self.params[nargs_out[self.command]:])
        if a1:
            return "%s %s %s\r\n" % (self.command, a1, a2)
        return "%s %s\r\n" % (self.command, a2)
    raw = property(__unicode__)

    def __repr__(self):
        # Avoid logging the password
        if self.command == IrcString('PASS'):
            return '<OutMessage cmd=%s params=%s>' % (repr(self.command), repr(['********'])) 
        return '<OutMessage cmd=%s params=%s>' % (repr(self.command), repr(self.params)) 
