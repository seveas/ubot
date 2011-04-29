import ubot.exceptions
import ubot.irc
import ConfigParser, logging, logging.config, os, re

class UbotConfig(object):
    def __init__(self, configfile):
        self.nicks       = []
        self.peers       = []
        self.servers     = []
        self.password    = None
        self.priority    = 1
        self.controlchan = None
        self.ident       = ubot.irc.IrcString('ubot')
        self.realname    = ubot.irc.IrcString('Ubot')
        self.busname     = 'ubot'
        self.parse_config(configfile)
        self.datadir     = os.path.expanduser(os.path.join('~','.local','share','ubot'))
        self.datafile    = os.path.join(self.datadir, self.busname + '.dat')

        # Configure logging
        logging.config.fileConfig(configfile)

    def parse_config(self, configfile):
        parser = ConfigParser.ConfigParser()
        parser.read(configfile)
        if not parser.has_section('me'):
            raise ubot.exceptions.ConfigError("No configuration found")
        i = 1
        while True:
            if not parser.has_option('me', 'nick' + str(i)):
                break
            self.nicks.append(ubot.irc.IrcString(parser.get('me', 'nick' + str(i))))
            i += 1
        if not self.nicks:
            raise ubot.exceptions.ConfigError("No nicknames found")
        i = 1
        while True:
            if not parser.has_option('me', 'server' + str(i)):
                break
            self.servers.append(parser.get('me', 'server' + str(i)))
            i += 1
        if not self.servers:
            raise ubot.exceptions.ConfigError("No servers found")
        for opt in ('ident', 'priority', 'password', 'realname', 'busname', 'controlchan'):
            if parser.has_option('me', opt):
                setattr(self, opt, parser.get('me', opt))
        self.ident = ubot.irc.IrcString(self.ident)
        self.realname = ubot.irc.IrcString(self.realname)
        self.controlchan = ubot.irc.IrcString(self.controlchan)
        self.priority = int(self.priority)

        # Parse peers
        i = 1
        while True:
            if not parser.has_section('peer' + str(i)):
                break
            self.peers.append(UbotPeer(parser, 'peer' + str(i)))
            i += 1

class UbotPeer(object):
    def __init__(self, config, section):
        self.is_active = False
        self.name = section
        if config.has_option(section, 'nickmatch'):
            self.nickmatch = re.compile(config.get(section, 'nickmatch'), re.I)
        else:
            raise ubot.exceptions.ConfigError("No nickmatch specified for %s" % section)
        if config.has_option(section, 'priority'):
            self.priority = int(config.get(section, 'priority'))
        else:
            raise ubot.exceptions.ConfigError("No priority specified for %s" % section)

    def isme(self, msg):
        return self.nickmatch.match(msg.prefix) != None
