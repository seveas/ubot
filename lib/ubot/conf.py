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

def configure(conffile):
    import ubot.autoconf as autoconf
    import shutil
    j = os.path.join
    # Get some user input
    print "It looks like you never ran ubot before, let's get started on configuring"
    print "I need to ask you a few questions first"
    def ask(question, default=""):
        sdefault = ""
        if default:
            sdefault = "[%s] " % default
        return raw_input(question + '? ' + sdefault).strip() or default
    def replace(data, vars):
        for var in vars.keys():
            if isinstance(vars[var], basestring):
                data = data.replace('$' + var, vars[var])
        return data

    confdir = os.path.dirname(conffile)
    conffile = os.path.basename(conffile)
    botname = ask("What is the name of your bot", os.path.splitext(conffile)[0])
    datadir = os.path.expanduser(ask("Where do you want to store the bot's data", "~/.local/share/ubot/"))
    server = ask("Which server will you connect to", "irc.freenode.net")
    password = ask("What is your password on that server")
    controlchannel = ask("Which channel will you be using to control the bot")
    commandchar = ask("Which character do you want to use as a prefix for commands", "@")

    vars = locals()

    # Create some directories
    if not os.path.exists(confdir):
        os.makedirs(confdir)
    if not os.path.exists(os.path.join(confdir, 'services')):
        os.makedirs(os.path.join(confdir, 'services'))
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    # First write dbus config
    src = j(autoconf.datadir,'session.conf')
    dst = j(confdir, 'session.conf')
    if not os.path.exists(dst) or (ask("session.conf already exists, overwrite", "N").lower() == 'y'):
        open(dst, 'w').write(replace(open(src).read(), vars))

    # Then main bot
    src = j(autoconf.datadir,'ubot.conf')
    dst = j(os.path.join(confdir,conffile))
    if not os.path.exists(dst) or (ask("%s already exists, overwrite" % conffile, "N").lower() == 'y'):
        open(dst, 'w').write(replace(open(src).read(), vars))

    # And helpers
    for helper in os.listdir(j(autoconf.datadir, 'helpers')):
        hd = j(autoconf.datadir, 'helpers', helper)
        src = j(hd, '%s.conf' % helper)
        dst = j(confdir, '%s.conf' % helper)
        if not os.path.exists(dst):
            open(dst, 'w').write(replace(open(src).read(), vars))

        dst2 = j(confdir, 'services', '%s.service' % helper)
        if not os.path.exists(dst2):
            open(dst2, 'w').write("""[D-BUS Service]
Name=net.seveas.ubot.helper.%s
Exec=%s/%s -c %s""" % (helper, autoconf.libexecdir, helper, dst))

        datafiles = [x for x in os.listdir(hd) if x != '%s.conf' % helper]
        if datafiles:
            if not os.path.exists(j(datadir, helper)):
                os.mkdir(j(datadir, helper))
            for f in datafiles:
                src = j(hd, f)
                dst = j(datadir, helper, f)
                if not os.path.exists(dst):
                    shutil.copy(src, dst)
