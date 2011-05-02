module Irc

class IrcString < String
    def %(args) return IrcString.new super end
    def +(args) return IrcString.new super end
    def ==(other) return self.downcase.to_s == IrcString.new(other).downcase end
    def <=>(other) return self.downcase.to_s <=> IrcString.new(other).downcase end
    def casecmp(other) return self.downcase.to_s.casecmp(IrcString.new(other).downcase) end
    def =~(obj) return self.downcase.to_s =~ obj end
    def count(*args)
        args = args.map {|str| IrcString.new(str).downcase }
        return self.downcase.to_s.count(*args)
    end
    def end_with?(*args)
        args = args.map {|str| IrcString.new(str).downcase }
        return self.downcase.to_s.end_with?(*args)
    end
    def eql(other) return self.downcase.to_s.eql(IrcString.new(other).downcase) end
    def hash() return self.downcase.to_s.hash end
    def include?(other) return self.downcase.to_s.include?(IrcString.new(other).downcase) end
    #def index? end
    #def rindex end
    def start_with?(*args)
        args = args.map {|str| IrcString.new(str).downcase }
        return self.downcase.to_s.start_with?(*args)
    end

    # For some reason, to translate a backslash, or to a backslash, one needs 4
    # of them. This seems to be a bug in ruby.
    def downcase() return IrcString.new(super.tr('[]\\\\~','{}|^')) end
    def downcase!() return super.tr!('[]\\\\~','{}|^') end
    def upcase() return IrcString.new(super.tr('{}|^','[]\\\\~')) end
    def upcase!() return super.tr!('{}|^','[]\\\\~') end
    def swapcase() return IrcString.new(super.tr('[]\\\\~{}|^','{}|^[]\\\\~')) end
    def swapcase!() return super.tr!('[]\\\\~{}|^','{}|^[]\\\\~') end
end

class OutMessage
    attr_reader :command, :params
    def initialize(command, params)
        @command = command
        @params = params
    end
end

class InMessage
    attr_reader :prefix, :command, :target, :params, :nick, :ident, :host
    attr_accessor :helper, :_command
    def initialize(prefix, command, target, params)
        @prefix = prefix
        @command = command
        @target = target
        @params = params
        if prefix =~ /^(.*)!(.*)@(.*)$/
            @nick = $1
            @ident = $2
            @host = $3
        end
        if Irc::Replies.member?(command)
            @ncommand = @command
            @command = Irc::Replies[@command]
        end
    end

    def is_ctcp
        return @command == 'PRIVMSG' && @params[-1] =~ /^\x01.*\x01$/
    end

    def is_action
        return @command == 'PRIVMSG' && @params[-1] =~ /^\x01ACTION.*\x01$/
    end

    def reply(message, action=false, private=false, slow=false)
        target = private ? @nick : @target
        @helper.send(target, message, action, slow)
    end
end

Has_target = ['PRIVMSG', 'NOTICE', 'PART', 'JOIN', 'KICK']

# Number of arguments that don't need to be prefixed with a :
Nargs_out = {
    'USER' =>    3,
    'TOPIC' =>   1,
    'KICK' =>    2,
    'PRIVMSG' => 1,
    'NOTICE' =>  1,
    'AWAY' =>    0,
    'PONG' =>    0,
    'PART' =>    1,
    'QUIT' =>    0,
    'SERVICE' => 4,
    'SQUIT' =>   1,
    'SQUERY' =>  1,
    'KILL' =>    1,
    'ERROR' =>   0,
    'AWAY' =>    0,
    'WALLOPS' => 0,
}
Nargs_in = {
    'JOIN' =>     0,
    'PONG' =>     1,
    'NOTICE' =>   1,
    'PRIVMSG' =>  1,
    'PING' =>     0,
    'PART' =>     1,
    'QUIT' =>     0,
    'ERROR' =>    0,
    'KICK' =>     2,
    'TOPIC' =>    1,

    # For RPL_ replies, first parameter is not counted
    'RPL_WELCOME' =>       0,
    'RPL_YOURHOST' =>      0,
    'RPL_CREATED' =>       0,
    'RPL_USERHOST' =>      0,
    'RPL_ISON' =>          0,
    'RPL_AWAY' =>          1,
    'RPL_UNAWAY' =>        1,
    'RPL_NOWAWAY' =>       1,
    'RPL_WHOISUSER' =>     4,
    'RPL_WHOISSERVER' =>   2,
    'RPL_WHOISOPERATOR' => 1,
    'RPL_WHOISIDLE' =>     2,
    'RPL_ENDOFWHOIS' =>    1,
    'RPL_WHOISCHANNELS' => 1,
    'RPL_WHOWASUSER' =>    4,
    'RPL_ENDOFWHOWAS' =>   1,
    'RPL_LIST' =>          2,
    'RPL_LISTEND' =>       0,
    'RPL_NOTOPIC' =>       1,
    'RPL_TOPIC' =>         1,
    'RPL_SUMMONING' =>     1,
    'RPL_ENDOFINVITELIST' => 1,
    'RPL_ENDOFEXCEPTLIST' => 1,
    'RPL_VERSION' =>       2,
    'RPL_WHOREPLY' =>      6,
    'RPL_ENDOFWHO' =>      1,
    'RPL_NAMREPLY' =>      2,
    'RPL_ENDOFNAMES' =>    1,
    'RPL_LINKS' =>         2,
    'RPL_ENDOFLINKS' =>    1,
    'RPL_ENDOFBANLIST' =>  1,
    'RPL_INFO' =>          0,
    'RPL_ENDOFINFO' =>     0,
    'RPL_MOTDSTART' =>     0,
    'RPL_MOTD' =>          0,
    'RPL_ENDOFMOTD' =>     0,
    'RPL_YOUREOPER' =>     0,
    'RPL_REHASHING' =>     1,
    'RPL_YOURESERVICE' =>  0,
    'RPL_TIME' =>          1,
    'RPL_USERSSTART' =>    0,
    'RPL_USERS' =>         0,
    'RPL_ENDOFUSERS' =>    0,
    'RPL_NOUSERS' =>       0,
    'RPL_ENDOFSTATS' =>    1,
    'RPL_STATSUPTIME' =>   0,
    'RPL_SERVLISTEND' =>   2,
    'RPL_LUSERCLIENT' =>   0,
    'RPL_LUSEROP' =>       1,
    'RPL_LUSERUNKNOWN' =>  1,
    'RPL_LUSERCHANNELS' => 1,
    'RPL_LUSERME' =>       0,
    'RPL_ADMINME' =>       1,
    'RPL_ADMINLOC1' =>     0,
    'RPL_ADMINLOC2' =>     0,
    'RPL_ADMINEMAIL' =>    0,
    'RPL_TRYAGAIN' =>      1,
    # Non-rfc ones
    'RPL_STATSCONN' =>     1,
    'RPL_LOCALUSERS' =>    1,
    'RPL_GLOBALUSERS' =>   1,

    # For ERR_ replies, first parameter is not counted
    'ERR_NOCHANMODES' =>      1,
    'ERR_NOSUCHNICK' =>       1,
    'ERR_NOSUCHSERVER' =>     1,
    'ERR_NOSUCHCHANNEL' =>    1,
    'ERR_CANNOTSENDTOCHAN' => 1,
    'ERR_TOOMANYCHANNELS' =>  1,
    'ERR_WASNOSUCHNICK' =>    1,
    'ERR_TOOMANYTARGETS' =>   1,
    'ERR_NOSUCHSERVICE' =>    1,
    'ERR_NOORIGIN' =>         0,
    'ERR_NORECIPIENT' =>      0,
    'ERR_NOTEXTTOSEND' =>     0,
    'ERR_NOTOPLEVEL' =>       1,
    'ERR_WILDTOPLEVEL' =>     1,
    'ERR_BADMASK' =>          1,
    'ERR_UNKNOWNCOMMAND' =>   1,
    'ERR_NOMOTD' =>           0,
    'ERR_NOADMININFO' =>      1,
    'ERR_FILEERROR' =>        0,
    'ERR_NONICKNAMEGIVEN' =>  0,
    'ERR_ERRONEUSNICKNAME' => 1,
    'ERR_NICKNAMEINUSE' =>    1,
    'ERR_NICKCOLLISION' =>    1,
    'ERR_UNAVAILRESOURCE' =>  1,
    'ERR_USERNOTINCHANNEL' => 2,
    'ERR_NOTONCHANNEL' =>     1,
    'ERR_USERONCHANNEL' =>    2,
    'ERR_NOLOGIN' =>          1,
    'ERR_SUMMONDISABLED' =>   0,
    'ERR_USERSDISABLED' =>    0,
    'ERR_NOTREGISTERED' =>    0,
    'ERR_NEEDMOREPARAMS' =>   1,
    'ERR_ALREADYREGISTRED' => 0,
    'ERR_NOPERMFORHOST' =>    0,
    'ERR_PASSWDMISMATCH' =>   0,
    'ERR_YOUREBANNEDCREEP' => 0,
    'ERR_YOUWILLBEBANNED' =>  0,
    'ERR_KEYSET' =>           1,
    'ERR_CHANNELISFULL' =>    1,
    'ERR_UNKNOWNMODE' =>      1,
    'ERR_INVITEONLYCHAN' =>   1,
    'ERR_BANNEDFROMCHAN' =>   1,
    'ERR_BADCHANNELKEY' =>    1,
    'ERR_BADCHANMASK' =>      1,
    'ERR_NOCHANMODES' =>      1,
    'ERR_BANLISTFULL' =>      2,
    'ERR_NOPRIVILEGES' =>     0,
    'ERR_CHANOPRIVSNEEDED' => 1,
    'ERR_CANTKILLSERVER' =>   0,
    'ERR_RESTRICTED' =>       0,
    'ERR_UNIQOPPRIVSNEEDED' => 0,
    'ERR_NOOPERHOST' =>       0,
    'ERR_UMODEUNKNOWNFLAG' => 0,
    'ERR_USERSDONTMATCH' =>   0,
}

# Straight from the RFC
Replies =  {
    '401' =>    'ERR_NOSUCHNICK',
    '402' =>    'ERR_NOSUCHSERVER',
    '403' =>    'ERR_NOSUCHCHANNEL',
    '404' =>    'ERR_CANNOTSENDTOCHAN',
    '405' =>    'ERR_TOOMANYCHANNELS',
    '406' =>    'ERR_WASNOSUCHNICK',
    '407' =>    'ERR_TOOMANYTARGETS',
    '408' =>    'ERR_NOSUCHSERVICE',
    '409' =>    'ERR_NOORIGIN',
    '411' =>    'ERR_NORECIPIENT',
    '412' =>    'ERR_NOTEXTTOSEND',
    '413' =>    'ERR_NOTOPLEVEL',
    '414' =>    'ERR_WILDTOPLEVEL',
    '415' =>    'ERR_BADMASK',
    '421' =>    'ERR_UNKNOWNCOMMAND',
    '422' =>    'ERR_NOMOTD',
    '423' =>    'ERR_NOADMININFO',
    '424' =>    'ERR_FILEERROR',
    '431' =>    'ERR_NONICKNAMEGIVEN',
    '432' =>    'ERR_ERRONEUSNICKNAME',
    '433' =>    'ERR_NICKNAMEINUSE',
    '436' =>    'ERR_NICKCOLLISION',
    '437' =>    'ERR_UNAVAILRESOURCE',
    '441' =>    'ERR_USERNOTINCHANNEL',
    '442' =>    'ERR_NOTONCHANNEL',
    '443' =>    'ERR_USERONCHANNEL',
    '444' =>    'ERR_NOLOGIN',
    '445' =>    'ERR_SUMMONDISABLED',
    '446' =>    'ERR_USERSDISABLED',
    '451' =>    'ERR_NOTREGISTERED',
    '461' =>    'ERR_NEEDMOREPARAMS',
    '462' =>    'ERR_ALREADYREGISTRED',
    '463' =>    'ERR_NOPERMFORHOST',
    '464' =>    'ERR_PASSWDMISMATCH',
    '465' =>    'ERR_YOUREBANNEDCREEP',
    '466' =>    'ERR_YOUWILLBEBANNED',
    '467' =>    'ERR_KEYSET',
    '471' =>    'ERR_CHANNELISFULL',
    '472' =>    'ERR_UNKNOWNMODE',
    '473' =>    'ERR_INVITEONLYCHAN',
    '474' =>    'ERR_BANNEDFROMCHAN',
    '475' =>    'ERR_BADCHANNELKEY',
    '476' =>    'ERR_BADCHANMASK',
    '477' =>    'ERR_NOCHANMODES',
    '478' =>    'ERR_BANLISTFULL',
    '481' =>    'ERR_NOPRIVILEGES',
    '482' =>    'ERR_CHANOPRIVSNEEDED',
    '483' =>    'ERR_CANTKILLSERVER',
    '484' =>    'ERR_RESTRICTED',
    '485' =>    'ERR_UNIQOPPRIVSNEEDED',
    '491' =>    'ERR_NOOPERHOST',
    '501' =>    'ERR_UMODEUNKNOWNFLAG',
    '502' =>    'ERR_USERSDONTMATCH',
    '300' =>    'RPL_NONE',
    '302' =>    'RPL_USERHOST',
    '303' =>    'RPL_ISON',
    '301' =>    'RPL_AWAY',
    '305' =>    'RPL_UNAWAY',
    '306' =>    'RPL_NOWAWAY',
    '311' =>    'RPL_WHOISUSER',
    '312' =>    'RPL_WHOISSERVER',
    '313' =>    'RPL_WHOISOPERATOR',
    '317' =>    'RPL_WHOISIDLE',
    '318' =>    'RPL_ENDOFWHOIS',
    '319' =>    'RPL_WHOISCHANNELS',
    '314' =>    'RPL_WHOWASUSER',
    '369' =>    'RPL_ENDOFWHOWAS',
    '321' =>    'RPL_LISTSTART',
    '322' =>    'RPL_LIST',
    '323' =>    'RPL_LISTEND',
    '324' =>    'RPL_CHANNELMODEIS',
    '331' =>    'RPL_NOTOPIC',
    '332' =>    'RPL_TOPIC',
    '341' =>    'RPL_INVITING',
    '342' =>    'RPL_SUMMONING',
    '346' =>    'RPL_INVITELIST',
    '347' =>    'RPL_ENDOFINVITELIST',
    '348' =>    'RPL_EXCEPTLIST',
    '349' =>    'RPL_ENDOFEXCEPTLIST',
    '351' =>    'RPL_VERSION',
    '352' =>    'RPL_WHOREPLY',
    '315' =>    'RPL_ENDOFWHO',
    '353' =>    'RPL_NAMREPLY',
    '366' =>    'RPL_ENDOFNAMES',
    '364' =>    'RPL_LINKS',
    '365' =>    'RPL_ENDOFLINKS',
    '367' =>    'RPL_BANLIST',
    '368' =>    'RPL_ENDOFBANLIST',
    '371' =>    'RPL_INFO',
    '374' =>    'RPL_ENDOFINFO',
    '375' =>    'RPL_MOTDSTART',
    '372' =>    'RPL_MOTD',
    '376' =>    'RPL_ENDOFMOTD',
    '381' =>    'RPL_YOUREOPER',
    '382' =>    'RPL_REHASHING',
    '383' =>    'RPL_YOURESERVICE',
    '391' =>    'RPL_TIME',
    '392' =>    'RPL_USERSSTART',
    '393' =>    'RPL_USERS',
    '394' =>    'RPL_ENDOFUSERS',
    '395' =>    'RPL_NOUSERS',
    '200' =>    'RPL_TRACELINK',
    '201' =>    'RPL_TRACECONNECTING',
    '202' =>    'RPL_TRACEHANDSHAKE',
    '203' =>    'RPL_TRACEUNKNOWN',
    '204' =>    'RPL_TRACEOPERATOR',
    '205' =>    'RPL_TRACEUSER',
    '206' =>    'RPL_TRACESERVER',
    '207' =>    'RPL_TRACESERVICE',
    '208' =>    'RPL_TRACENEWTYPE',
    '209' =>    'RPL_TRACECLASS',
    '210' =>    'RPL_TRACERECONNECT',
    '261' =>    'RPL_TRACELOG',
    '262' =>    'RPL_TRACEEND',
    '211' =>    'RPL_STATSLINKINFO',
    '212' =>    'RPL_STATSCOMMANDS',
    '213' =>    'RPL_STATSCLINE',
    '214' =>    'RPL_STATSNLINE',
    '215' =>    'RPL_STATSILINE',
    '216' =>    'RPL_STATSKLINE',
    '218' =>    'RPL_STATSYLINE',
    '219' =>    'RPL_ENDOFSTATS',
    '241' =>    'RPL_STATSLLINE',
    '242' =>    'RPL_STATSUPTIME',
    '243' =>    'RPL_STATSOLINE',
    '244' =>    'RPL_STATSHLINE',
    '221' =>    'RPL_UMODEIS',
    '234' =>    'RPL_SERVLIST',
    '235' =>    'RPL_SERVLISTEND',
    '251' =>    'RPL_LUSERCLIENT',
    '252' =>    'RPL_LUSEROP',
    '253' =>    'RPL_LUSERUNKNOWN',
    '254' =>    'RPL_LUSERCHANNELS',
    '255' =>    'RPL_LUSERME',
    '256' =>    'RPL_ADMINME',
    '257' =>    'RPL_ADMINLOC1',
    '258' =>    'RPL_ADMINLOC2',
    '259' =>    'RPL_ADMINEMAIL',
    '263' =>    'RPL_TRYAGAIN',
    '001' =>    'RPL_WELCOME',
    '002' =>    'RPL_YOURHOST',
    '003' =>    'RPL_CREATED',
    '004' =>    'RPL_MYINFO',
    '005' =>    'RPL_BOUNCE',
}
Nonrfc_replies = {
    # Seen on freenode/hyperion (there are several more)
    '333' =>    'RPL_TOPICWHOTIME',
    '250' =>    'RPL_STATSCONN',
    '265' =>    'RPL_LOCALUSERS',
    '266' =>    'RPL_GLOBALUSERS',
}
Replies.update(Nonrfc_replies)

Channel_user_modes = {
    'o' => '@',
    'h' => '%',
    'v' => '+',
}
end
