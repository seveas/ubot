require 'dbus'
require 'digest/sha1'
require 'ini'
require 'optparse'
require 'ubot/rfc2812'

module Ubot
    class Helper < DBus::Object
        attr_accessor :runloop

        # We need to delay initialization because we do not know the name yet
        alias :dbus_initialize initialize

        # We redefine send, so make the old one available
        alias :call send
        def initialize
        end

        def add_options(parser, options)
            options[:address] = 'tcp:host=localhost,port=11235'
            options[:name] = nil
            options[:config] = nil
            parser.on('-a', '--address ADDRESS', 'The address of your session bus') { |address| options[:address] = address }
            parser.on('-n', '--name NAME', 'DBus name for your helper') { |name| options[:name] = name }
            parser.on('-c', '--config FILE', 'Configuration file') { |file| options[:config] = File.expand_path(file) }
        end

        def handle_options(options)
            if options[:name]
                @name = options[:name]
            else
                @name = self.class.to_s.downcase.gsub(/(.*::)?(.*?)((comma|respo)nder)?$/, '\2')
            end
            if options[:config]
                if File.exist?(options[:config])
                    @conf = Ini.new(options[:config])
                else
                    raise ArgumentError, "Configfile does not exist"
                end
            else
                raise ArgumentError, "No configfile specified"
            end

            @busname = @conf[@name]['busname'] || @name
            if @busname !~ /\./
                @busname = 'net.seveas.ubot.helper.' + @busname
            end
            @busobjname = '/' + @busname.gsub(/\./, '/')
            service = DBus::session_bus.request_service(@busname)
            dbus_initialize(@busobjname)
            service.export(self)

            @botname = @conf[@name]['botname'] || 'ubot'
            get_bot

            # Detect bot exits/reconnects
            bus = DBus::session_bus.service('org.freedesktop.DBus').object('/org/freedesktop/DBus')
            bus.introspect
            bus['org.freedesktop.DBus'].on_signal(DBus::session_bus,'NameOwnerChanged') do |name,old,new|
                if name == 'net.seveas.ubot.' + @botname
                    get_bot
                end
            end
        end

        def get_bot
            @bots = DBus::session_bus.service('net.seveas.ubot.' + @botname)
            @bot = @bots.object('/net/seveas/ubot/' + @botname)
            @bot.introspect
            @bot.default_iface = 'net.seveas.ubot'

            @bot.on_signal('message_sent') do |command,params|
                message_sent(command, params)
            end
            @bot.on_signal('message_received') do |prefix,command,target,params|
                message_received(prefix,command,target,params)
            end
            @bot.on_signal('sync_complete') do
                sync_complete
            end
            @bot.on_signal('master_change') do |am_master|
                @master = am_master
            end
            @bot.on_signal('exiting') do
                @runloop.quit
            end

            info = @bot.get_info[0]
            @bot_version = info['version']
            @master = info['master']
            @synced = info['synced']
            @nickname = info['nickname']
            if @synced
                sync_complete
            end
        end

        def message_sent(command, params)
            message = OutMessage.new(command, params)
            command.downcase!
            if respond_to?('out_' + command)
                call('out_' + command, message)
            end
        end

        def message_received(prefix, command, target, params)
            message = InMessage.new(prefix, command, target, params)
            message.helper = self
            command.sub!(/^(CMD|RPL)_/, '')
            command.downcase!
            if respond_to?('_in_' + command)
                call('_in_' + command, message)
            end
            if respond_to?('in_' + command)
                call('in_' + command, message)
            end
        end

        def sync_complete
            @synced = 1
            @channels = Hash[ 
                @bot.get_channels[0].map {|c|
                    [c, @bots.object('/net/seveas/ubot/%s/channel/%s' % [@botname, escape_object_path(c)])]
                } 
            ]
            @channels.each_value { |c| c.introspect; c.default_iface = 'net.seveas.ubot.channel' }
        end

        def _in_part(message)
            if message.prefix.start_with?(@nick + '!')
                @channels.delete(message.target)
            end
        end

        def _in_join(message)
            if message.prefix.start_with?(@nick + '!')
                @channels[message.target] = @bots.object('/net/seveas/ubot/%s/channel/%s' % [@botname, escape_object_path(c)])
                @channels[message.target].introspect
                @channels[message.target].default_iface = 'net.seveas.ubot.channel'
            end
        end

        def _in_nick(message)
            if message.prefix.start_with?(@nick + '!')
                @nickname = message.params[0]
            end
        end

        def addressed(message)
            return @synced && @master
        end

        def error(msg)
            @bot.log(@name, 'ERROR', msg)
        end

        def warning(msg)
            @bot.log(@name, 'WARNING', msg)
        end

        def info(msg)
            @bot.log(@name, 'INFO', msg)
        end

        def debug(msg)
            @bot.log(@name, 'DEBUG', msg)
        end

        def self.run
            this = new
            options = {}
            optparse = OptionParser.new do |parser|
                this.add_options(parser, options)
            end
            optparse.parse!
            this.handle_options(options)
            this.info("helper started")
            this.runloop = DBus::Main.new()
            this.runloop << DBus::session_bus
            this.runloop.run()
            if this.respond_to?('exit')
                this.exit
            end
        end

        dbus_interface 'net.seveas.ubot.helper' do
            dbus_method :quit do
                @runloop.quit
            end
            dbus_method :get_info, "out info:a{ss}" do
                @helper_info
            end
        end

    end

    class Responder < Helper
        def handle_options(options)
            super
            @active_channels = (@conf[@name]['channels'] || '').split(',')
            @respond_to_all = @active_channels.member?('all')
            @respond_to_private = @respond_to_all || @active_channels.member?(@name)
        end

        def addressed(message)
            return false unless super
            if message.target == @nickname
                return @respond_to_private
            end
            return @respond_to_all || @active_channels.member?(message.target)
        end

        def send(target, message, action=false, slow=false)
            if target.start_with?('#')
                if action
                    if slow
                        @channels[target].slowdo(message)
                    else
                        @channels[target].do(message)
                    end
                else
                    if slow
                        @channels[target].slowsay(message)
                    else
                        @channels[target].say(message)
                    end
                end
            else
                if action
                    if slow
                        @bot.slowdo(target, message)
                    else
                        @bot.do(target, message)
                    end
                else
                    if slow
                        @bot.slowsay(target, message)
                    else
                        @bot.say(target, message)
                    end
                end
            end
        end
    end

    class Commander < Responder
        def handle_options(options)
            super
            @prefix = @conf[@name]['prefix'] || '@'
        end

        def addressed(message)
            return false unless super
            msg = message.params[0].strip()
            _addressed = false
            @prefix.each_char do |char|
                if msg.start_with?(char)
                    _addressed = true
                    msg.gsub!(/^.\s*/, '')
                    break
                end
            end
            return false unless _addressed

            # So, prefix was seen (FIXME: allow nickname as prefix)
            # Now for the commands
            if @commands
                command, arg = msg.split(nil,2)
                arg ||= ''
                if @commands.member?(command)
                    message._command = [@commands[command], arg]
                    info("%s was called in %s by %s with argument %s" % [command, message.target, message.prefix, arg])
                    return true
                else
                    return false
                end
            end
            # If a plugin doesn't define a command list, assume it'll do
            # its own argument handling
            return true
        end

        def in_privmsg(message)
            if addressed(message)
                command, arg = message._command
                call(command, message, arg)
            end
        end

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
            if Rfc2812::Replies.member?(command)
                @ncommand = @command
                @command = Rfc2812::Replies[@command]
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
end

def escape_object_path(path)
    return path.gsub(/[^a-zA-Z0-9]/) { |match| '_' + match[0].ord.to_s }
end

# Work around some limitations in version 0.3 of the dbus bindings
def hex(arg)
    return arg.to_s.split(//).collect { |a| "%x" % a[0].ord }.join
end
def unhex(arg)
    return arg.to_s.scan(/../).collect { |a| eval('0x%s' % a).chr }.join
end
module DBus
  # UBOT: add tcp connection support
  class Connection
    def parse_session_string
      path_parsed = /^([^:]*):([^;]*)$/.match(@path)
      @transport = path_parsed[1]
      adr = path_parsed[2]
      if @transport == "unix"
        adr.split(",").each do |eqstr|
          idx, val = eqstr.split("=")
          case idx
          when "path"
            @type = idx
            @unix = val
          when "abstract"
            @type = idx
            @unix_abstract = val
          when "guid"
            @guid = val
          end
        end
      # BEGIN UBOT CODE
      elsif @transport == "tcp"
        adr.split(",").each do |eqstr|
          idx, val = eqstr.split("=")
          case idx
          when "host"
            @host = val
          when "port"
            @port = val
          when "guid"
            @guid = val
          end
        end
      # END UBOT CODE
      end
    end

    def connect
      parse_session_string
      if @transport == "unix" and @type == "abstract"
        if HOST_END == LIL_END
          sockaddr = "\1\0\0#{@unix_abstract}"
        else
          sockaddr = "\0\1\0#{@unix_abstract}"
        end
      elsif @transport == "unix" and @type == "path"
        sockaddr = Socket.pack_sockaddr_un(@unix)
      # BEGIN UBOT CODE
      elsif @transport == "tcp"
        @socket = Socket.new(Socket::Constants::PF_INET,
                             Socket::Constants::SOCK_STREAM, 0)
        sockaddr = Socket.pack_sockaddr_in(@port, @host)
      # END UBOT CODE
      end
      @socket.connect(sockaddr)
      init_connection
    end
  end

  class DBus::Client
    # UBOT: reorder some operations so multiple authentictors work
    def initialize(socket)
      @socket = socket
      @state = nil
      @auth_list = [DBus::External, DBus::Cookie]
    end

    # Start the authentication process.
    def authenticate
      @socket.write(0.chr)
      @state = :Starting
      next_authenticator
      while @state != :Authenticated
        r = next_state
        return r if not r
      end
      true
    end

    def next_authenticator
      raise DBus::AuthenticationFailed if @auth_list.size == 0
      @authenticator = @auth_list.shift.new
      @state = :WaitingForData
      send("AUTH", @authenticator.name, @authenticator.authenticate)
    end
end

# UBOT: Add DBUS_COOKIE_SHA1
class DBus::Cookie < DBus::External
   def name
        return 'DBUS_COOKIE_SHA1'
   end

   def data(busdata)
        scontext, sid, schallenge = unhex(busdata).split()
        filename = File.expand_path(File.join('~', '.dbus-keyrings', scontext))
        File.readlines(filename).each{ |line|
            id, time, cookie = line.split()
            if id == sid
                challenge = Digest::SHA1.hexdigest(Time.now().to_s)
                hash = Digest::SHA1.hexdigest("#{schallenge}:#{challenge}:#{cookie}")
                mydata = hex("#{challenge} #{hash}")
                return :AuthContinue, mydata
            end
        }
   end
end
end
