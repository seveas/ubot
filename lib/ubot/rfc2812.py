import sys

rfc2812_tolower = {ord('['):  u'{',
                   ord(']'):  u'}',
                   ord('\\'): u'|',
                   ord('~'):  u'^'}
rfc2812_toupper = {ord('{'):  u']',
                   ord('{'):  u'[',
                   ord('|'): u'\\',
                   ord('^'):  u'~'}

# Case-insensitive string
class IrcString(unicode):
    # Comparison
    def __cmp__(self, other):
        return isinstance(other, basestring) and cmp(unicode(self.lower()), unicode(other.lower()))
    def __lt__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) < unicode(other.lower())
    def __le__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) <= unicode(other.lower())
    def __gt__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) > unicode(other.lower())
    def __ge__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) >= unicode(other.lower())
    def __eq__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) == unicode(other.lower())
    def __ne__(self, other):
        return isinstance(other, basestring) and unicode(self.lower()) != unicode(other.lower())
    def __contains__(self, needle):
        return isinstance(needle, basestring) and unicode(needle.lower()) in unicode(self.lower())
    def __hash__(self):
        return hash(unicode(self).lower())
    def endswith(self, needle):
        return isinstance(needle, basestring) and unicode(self.lower()).endswith(unicode(needle.lower()))
    def startswith(self, needle):
        return isinstance(needle, basestring) and unicode(self.lower()).startswith(unicode(needle.lower()))

    # Searching and indexing
    def __getitem__(self, item):
        return IrcString(unicode(self).__getitem__(item))
    def __getslice__(self, i, j):
        return IrcString(unicode(self).__getslice__(i,j))
    def count(self, needle, start=0, end=sys.maxint):
        return unicode(self.lower()).count(needle.lower(), start, end)
    def find(self, needle, start=0, end=sys.maxint):
        return unicode(self.lower()).find(needle.lower(), start, end)
    def index(self, needle, start=0, end=sys.maxint):
        return unicode(self.lower()).index(needle.lower(), start, end)
    def rfind(self, needle, start=0, end=sys.maxint):
        return unicode(self.lower()).rfind(needle.lower(), start, end)
    def rindex(self, needle, start=0, end=sys.maxint):
        return unicode(self.lower()).rindex(needle.lower(), start, end)

    # Manipulation
    def __add__(self, other):
        return IrcString(unicode(self).__add__(other))
    def __mod__(self, other):
        return IrcString(unicode(self).__mod__(other))
    def __rmod__(self, other):
        return IrcString(unicode(self).__rmod__(other))
    def __mul__(self, other):
        return IrcString(unicode(self).__mul__(other))
    def __rmul__(self, other):
        return IrcString(unicode(self).__rmul__(other))
    def capitalize(self):
        return IrcString(unicode(self).capitalize)
    def center(self, width, fillchar=' '):
        return IrcString(unicode(self).center(width, fillchar))
    def decode(self, encoding=sys.getdefaultencoding(), errors='strict'):
        return IrcString(unicode(self).decode(encoding, errors))
    def encode(self, encoding=sys.getdefaultencoding(), errors='strict'):
        return IrcString(unicode(self).encode(encoding, errors))
    def expandtabs(self, tabsize=8):
        return IrcString(unicode(self).expandtabs(tabsize))
    def join(self, sequence):
        return IrcString(unicode(self).join(sequence))
    def ljust(self, width, fillchar=' '):
        return IrcString(unicode(self).ljust(width, fillchar))
    #def lower(self):
    #    return IrcString(unicode(self).lower())
    def lstrip(self, chars=None):
        return IrcString(unicode(self).lstrip(chars))
    def partition(self, sep):
        return [IrcString(x) for x in unicode(self).partition(sep)]
    def replace(self, old, new, maxsplit=sys.maxint):
        return IrcString(unicode(self).replace(old, new, maxsplit))
    def rjust(self, width, fillchar=' '):
        return IrcString(unicode(self).rjust(width, fillchar))
    def rpartition(self, sep):
        return [IrcString(x) for x in unicode(self).rpartition(sep)]
    def rsplit(self, sep=None, maxsplit=sys.maxint):
        return [IrcString(x) for x in unicode(self).rsplit(sep, maxsplit)]
    def rstrip(self, chars=None):
        return IrcString(unicode(self).rstrip(chars))
    def split(self, sep=None, maxsplit=sys.maxint):
        return [IrcString(x) for x in unicode(self).split(sep, maxsplit)]
    def splitlines(keepends=False):
        return [IrcString(x) for x in unicode(self).splitlines(keepends)]
    def strip(self, chars=None):
        return IrcString(unicode(self).strip(chars))
    def swapcase(self):
        return IrcString(unicode(self).swapcase())
    def title(self):
        return IrcString(unicode(self).title())
    def translate(self, table):
        return IrcString(unicode(self).translate(table))
    #def upper(self):
    #    return IrcString(unicode(self).upper())
    def zfill(width):
        return IrcString(unicode(self).zfill(width))

    def ireplace(self, old, new, count=sys.maxint):
        pos = 0
        replaced = 0
        ret = self
        while replaced < count:
            pos = self.find(old, pos)
            if pos == -1:
                break
            ret = ret[:pos] + new + ret[pos+len(old):]
            pos += len(new)
            replaced += 1
        return ret

    # RFC 2812 says:
    # Because of IRC's Scandinavian origin, the characters {}|^ are
    # considered to be the lower case equivalents of the characters []\~,
    # respectively.
    def lower(self):
        return IrcString(unicode(self).lower().translate(rfc2812_tolower))
    def upper(self):
        return IrcString(unicode(self).upper().translate(rfc2812_toupper))

s = IrcString

has_target = ('PRIVMSG', 'NOTICE', 'PART', 'JOIN', 'KICK')

# Number of arguments that don't need to be prefixed with a :
nargs_out = {
    s('USER'):    3,
    s('TOPIC'):   1,
    s('KICK'):    2,
    s('PRIVMSG'): 1,
    s('NOTICE'):  1,
    s('AWAY'):    0,
    s('PONG'):    0,
    s('PART'):    1,
    s('QUIT'):    0,
    s('SERVICE'): 4,
    s('SQUIT'):   1,
    s('SQUERY'):  1,
    s('KILL'):    1,
    s('ERROR'):   0,
    s('AWAY'):    0,
    s('WALLOPS'): 0,
}
nargs_in = {
    s('JOIN'):     0,
    s('PONG'):     1,
    s('NOTICE'):   1,
    s('PRIVMSG'):  1,
    s('PING'):     0,
    s('PART'):     1,
    s('QUIT'):     0,
    s('ERROR'):    0,
    s('KICK'):     2,
    s('TOPIC'):    1,

    # For RPL_ replies, first parameter is not counted
    s('RPL_WELCOME'):       0,
    s('RPL_YOURHOST'):      0,
    s('RPL_CREATED'):       0,
    s('RPL_USERHOST'):      0,
    s('RPL_ISON'):          0,
    s('RPL_AWAY'):          1,
    s('RPL_UNAWAY'):        1,
    s('RPL_NOWAWAY'):       1,
    s('RPL_WHOISUSER'):     4,
    s('RPL_WHOISSERVER'):   2,
    s('RPL_WHOISOPERATOR'): 1,
    s('RPL_WHOISIDLE'):     2,
    s('RPL_ENDOFWHOIS'):    1,
    s('RPL_WHOISCHANNELS'): 1,
    s('RPL_WHOWASUSER'):    4,
    s('RPL_ENDOFWHOWAS'):   1,
    s('RPL_LIST'):          2,
    s('RPL_LISTEND'):       0,
    s('RPL_NOTOPIC'):       1,
    s('RPL_TOPIC'):         1,
    s('RPL_SUMMONING'):     1,
    s('RPL_ENDOFINVITELIST'): 1,
    s('RPL_ENDOFEXCEPTLIST'): 1,
    s('RPL_VERSION'):       2,
    s('RPL_WHOREPLY'):      6,
    s('RPL_ENDOFWHO'):      1,
    s('RPL_NAMREPLY'):      2,
    s('RPL_ENDOFNAMES'):    1,
    s('RPL_LINKS'):         2,
    s('RPL_ENDOFLINKS'):    1,
    s('RPL_ENDOFBANLIST'):  1,
    s('RPL_INFO'):          0,
    s('RPL_ENDOFINFO'):     0,
    s('RPL_MOTDSTART'):     0,
    s('RPL_MOTD'):          0,
    s('RPL_ENDOFMOTD'):     0,
    s('RPL_YOUREOPER'):     0,
    s('RPL_REHASHING'):     1,
    s('RPL_YOURESERVICE'):  0,
    s('RPL_TIME'):          1,
    s('RPL_USERSSTART'):    0,
    s('RPL_USERS'):         0,
    s('RPL_ENDOFUSERS'):    0,
    s('RPL_NOUSERS'):       0,
    s('RPL_ENDOFSTATS'):    1,
    s('RPL_STATSUPTIME'):   0,
    s('RPL_SERVLISTEND'):   2,
    s('RPL_LUSERCLIENT'):   0,
    s('RPL_LUSEROP'):       1,
    s('RPL_LUSERUNKNOWN'):  1,
    s('RPL_LUSERCHANNELS'): 1,
    s('RPL_LUSERME'):       0,
    s('RPL_ADMINME'):       1,
    s('RPL_ADMINLOC1'):     0,
    s('RPL_ADMINLOC2'):     0,
    s('RPL_ADMINEMAIL'):    0,
    s('RPL_TRYAGAIN'):      1,
    # Non-rfc ones
    s('RPL_STATSCONN'):     1,
    s('RPL_LOCALUSERS'):    1,
    s('RPL_GLOBALUSERS'):   1,

    # For ERR_ replies, first parameter is not counted
    s('ERR_NOCHANMODES'):      1,
    s('ERR_NOSUCHNICK'):       1,
    s('ERR_NOSUCHSERVER'):     1,
    s('ERR_NOSUCHCHANNEL'):    1,
    s('ERR_CANNOTSENDTOCHAN'): 1,
    s('ERR_TOOMANYCHANNELS'):  1,
    s('ERR_WASNOSUCHNICK'):    1,
    s('ERR_TOOMANYTARGETS'):   1,
    s('ERR_NOSUCHSERVICE'):    1,
    s('ERR_NOORIGIN'):         0,
    s('ERR_NORECIPIENT'):      0,
    s('ERR_NOTEXTTOSEND'):     0,
    s('ERR_NOTOPLEVEL'):       1,
    s('ERR_WILDTOPLEVEL'):     1,
    s('ERR_BADMASK'):          1,
    s('ERR_UNKNOWNCOMMAND'):   1,
    s('ERR_NOMOTD'):           0,
    s('ERR_NOADMININFO'):      1,
    s('ERR_FILEERROR'):        0,
    s('ERR_NONICKNAMEGIVEN'):  0,
    s('ERR_ERRONEUSNICKNAME'): 1,
    s('ERR_NICKNAMEINUSE'):    1,
    s('ERR_NICKCOLLISION'):    1,
    s('ERR_UNAVAILRESOURCE'):  1,
    s('ERR_USERNOTINCHANNEL'): 2,
    s('ERR_NOTONCHANNEL'):     1,
    s('ERR_USERONCHANNEL'):    2,
    s('ERR_NOLOGIN'):          1,
    s('ERR_SUMMONDISABLED'):   0,
    s('ERR_USERSDISABLED'):    0,
    s('ERR_NOTREGISTERED'):    0,
    s('ERR_NEEDMOREPARAMS'):   1,
    s('ERR_ALREADYREGISTRED'): 0,
    s('ERR_NOPERMFORHOST'):    0,
    s('ERR_PASSWDMISMATCH'):   0,
    s('ERR_YOUREBANNEDCREEP'): 0,
    s('ERR_YOUWILLBEBANNED'):  0,
    s('ERR_KEYSET'):           1,
    s('ERR_CHANNELISFULL'):    1,
    s('ERR_UNKNOWNMODE'):      1,
    s('ERR_INVITEONLYCHAN'):   1,
    s('ERR_BANNEDFROMCHAN'):   1,
    s('ERR_BADCHANNELKEY'):    1,
    s('ERR_BADCHANMASK'):      1,
    s('ERR_NOCHANMODES'):      1,
    s('ERR_BANLISTFULL'):      2,
    s('ERR_NOPRIVILEGES'):     0,
    s('ERR_CHANOPRIVSNEEDED'): 1,
    s('ERR_CANTKILLSERVER'):   0,
    s('ERR_RESTRICTED'):       0,
    s('ERR_UNIQOPPRIVSNEEDED'): 0,
    s('ERR_NOOPERHOST'):       0,
    s('ERR_UMODEUNKNOWNFLAG'): 0,
    s('ERR_USERSDONTMATCH'):   0,
}

# Straight from the RFC
replies =  {
    '401':    s('ERR_NOSUCHNICK'),
    '402':    s('ERR_NOSUCHSERVER'),
    '403':    s('ERR_NOSUCHCHANNEL'),
    '404':    s('ERR_CANNOTSENDTOCHAN'),
    '405':    s('ERR_TOOMANYCHANNELS'),
    '406':    s('ERR_WASNOSUCHNICK'),
    '407':    s('ERR_TOOMANYTARGETS'),
    '408':    s('ERR_NOSUCHSERVICE'),
    '409':    s('ERR_NOORIGIN'),
    '411':    s('ERR_NORECIPIENT'),
    '412':    s('ERR_NOTEXTTOSEND'),
    '413':    s('ERR_NOTOPLEVEL'),
    '414':    s('ERR_WILDTOPLEVEL'),
    '415':    s('ERR_BADMASK'),
    '421':    s('ERR_UNKNOWNCOMMAND'),
    '422':    s('ERR_NOMOTD'),
    '423':    s('ERR_NOADMININFO'),
    '424':    s('ERR_FILEERROR'),
    '431':    s('ERR_NONICKNAMEGIVEN'),
    '432':    s('ERR_ERRONEUSNICKNAME'),
    '433':    s('ERR_NICKNAMEINUSE'),
    '436':    s('ERR_NICKCOLLISION'),
    '437':    s('ERR_UNAVAILRESOURCE'),
    '441':    s('ERR_USERNOTINCHANNEL'),
    '442':    s('ERR_NOTONCHANNEL'),
    '443':    s('ERR_USERONCHANNEL'),
    '444':    s('ERR_NOLOGIN'),
    '445':    s('ERR_SUMMONDISABLED'),
    '446':    s('ERR_USERSDISABLED'),
    '451':    s('ERR_NOTREGISTERED'),
    '461':    s('ERR_NEEDMOREPARAMS'),
    '462':    s('ERR_ALREADYREGISTRED'),
    '463':    s('ERR_NOPERMFORHOST'),
    '464':    s('ERR_PASSWDMISMATCH'),
    '465':    s('ERR_YOUREBANNEDCREEP'),
    '466':    s('ERR_YOUWILLBEBANNED'),
    '467':    s('ERR_KEYSET'),
    '471':    s('ERR_CHANNELISFULL'),
    '472':    s('ERR_UNKNOWNMODE'),
    '473':    s('ERR_INVITEONLYCHAN'),
    '474':    s('ERR_BANNEDFROMCHAN'),
    '475':    s('ERR_BADCHANNELKEY'),
    '476':    s('ERR_BADCHANMASK'),
    '477':    s('ERR_NOCHANMODES'),
    '478':    s('ERR_BANLISTFULL'),
    '481':    s('ERR_NOPRIVILEGES'),
    '482':    s('ERR_CHANOPRIVSNEEDED'),
    '483':    s('ERR_CANTKILLSERVER'),
    '484':    s('ERR_RESTRICTED'),
    '485':    s('ERR_UNIQOPPRIVSNEEDED'),
    '491':    s('ERR_NOOPERHOST'),
    '501':    s('ERR_UMODEUNKNOWNFLAG'),
    '502':    s('ERR_USERSDONTMATCH'),
    '300':    s('RPL_NONE'),
    '302':    s('RPL_USERHOST'),
    '303':    s('RPL_ISON'),
    '301':    s('RPL_AWAY'),
    '305':    s('RPL_UNAWAY'),
    '306':    s('RPL_NOWAWAY'),
    '311':    s('RPL_WHOISUSER'),
    '312':    s('RPL_WHOISSERVER'),
    '313':    s('RPL_WHOISOPERATOR'),
    '317':    s('RPL_WHOISIDLE'),
    '318':    s('RPL_ENDOFWHOIS'),
    '319':    s('RPL_WHOISCHANNELS'),
    '314':    s('RPL_WHOWASUSER'),
    '369':    s('RPL_ENDOFWHOWAS'),
    '321':    s('RPL_LISTSTART'),
    '322':    s('RPL_LIST'),
    '323':    s('RPL_LISTEND'),
    '324':    s('RPL_CHANNELMODEIS'),
    '331':    s('RPL_NOTOPIC'),
    '332':    s('RPL_TOPIC'),
    '341':    s('RPL_INVITING'),
    '342':    s('RPL_SUMMONING'),
    '346':    s('RPL_INVITELIST'),
    '347':    s('RPL_ENDOFINVITELIST'),
    '348':    s('RPL_EXCEPTLIST'),
    '349':    s('RPL_ENDOFEXCEPTLIST'),
    '351':    s('RPL_VERSION'),
    '352':    s('RPL_WHOREPLY'),
    '315':    s('RPL_ENDOFWHO'),
    '353':    s('RPL_NAMREPLY'),
    '366':    s('RPL_ENDOFNAMES'),
    '364':    s('RPL_LINKS'),
    '365':    s('RPL_ENDOFLINKS'),
    '367':    s('RPL_BANLIST'),
    '368':    s('RPL_ENDOFBANLIST'),
    '371':    s('RPL_INFO'),
    '374':    s('RPL_ENDOFINFO'),
    '375':    s('RPL_MOTDSTART'),
    '372':    s('RPL_MOTD'),
    '376':    s('RPL_ENDOFMOTD'),
    '381':    s('RPL_YOUREOPER'),
    '382':    s('RPL_REHASHING'),
    '383':    s('RPL_YOURESERVICE'),
    '391':    s('RPL_TIME'),
    '392':    s('RPL_USERSSTART'),
    '393':    s('RPL_USERS'),
    '394':    s('RPL_ENDOFUSERS'),
    '395':    s('RPL_NOUSERS'),
    '200':    s('RPL_TRACELINK'),
    '201':    s('RPL_TRACECONNECTING'),
    '202':    s('RPL_TRACEHANDSHAKE'),
    '203':    s('RPL_TRACEUNKNOWN'),
    '204':    s('RPL_TRACEOPERATOR'),
    '205':    s('RPL_TRACEUSER'),
    '206':    s('RPL_TRACESERVER'),
    '207':    s('RPL_TRACESERVICE'),
    '208':    s('RPL_TRACENEWTYPE'),
    '209':    s('RPL_TRACECLASS'),
    '210':    s('RPL_TRACERECONNECT'),
    '261':    s('RPL_TRACELOG'),
    '262':    s('RPL_TRACEEND'),
    '211':    s('RPL_STATSLINKINFO'),
    '212':    s('RPL_STATSCOMMANDS'),
    '213':    s('RPL_STATSCLINE'),
    '214':    s('RPL_STATSNLINE'),
    '215':    s('RPL_STATSILINE'),
    '216':    s('RPL_STATSKLINE'),
    '218':    s('RPL_STATSYLINE'),
    '219':    s('RPL_ENDOFSTATS'),
    '241':    s('RPL_STATSLLINE'),
    '242':    s('RPL_STATSUPTIME'),
    '243':    s('RPL_STATSOLINE'),
    '244':    s('RPL_STATSHLINE'),
    '221':    s('RPL_UMODEIS'),
    '234':    s('RPL_SERVLIST'),
    '235':    s('RPL_SERVLISTEND'),
    '251':    s('RPL_LUSERCLIENT'),
    '252':    s('RPL_LUSEROP'),
    '253':    s('RPL_LUSERUNKNOWN'),
    '254':    s('RPL_LUSERCHANNELS'),
    '255':    s('RPL_LUSERME'),
    '256':    s('RPL_ADMINME'),
    '257':    s('RPL_ADMINLOC1'),
    '258':    s('RPL_ADMINLOC2'),
    '259':    s('RPL_ADMINEMAIL'),
    '263':    s('RPL_TRYAGAIN'),
    '001':    s('RPL_WELCOME'),
    '002':    s('RPL_YOURHOST'),
    '003':    s('RPL_CREATED'),
    '004':    s('RPL_MYINFO'),
    '005':    s('RPL_BOUNCE'),
}
nonrfc_replies = {
    # Seen on freenode/hyperion (there are several more)
    '333':    s('RPL_TOPICWHOTIME'),
    '250':    s('RPL_STATSCONN'),
    '265':    s('RPL_LOCALUSERS'),
    '266':    s('RPL_GLOBALUSERS'),
}
replies.update(nonrfc_replies)

channel_user_modes = {
    'o': '@',
    'h': '%',
    'v': '+',
}

del(s)
