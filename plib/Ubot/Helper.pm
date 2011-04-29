package Ubot::Helper;

use strict;
use warnings;
use Config::INI::Reader;
use Getopt::Long;
use Net::DBus;
use Net::DBus::Reactor;
use Net::DBus::Exporter qw(net.seveas.ubot.helper);

use base 'Net::DBus::Object';

sub new {
    my ($class) = @_;
    my $self = {};
    $self->{address} = $ENV{DBUS_STARTER_ADDRESS} || $ENV{DBUS_SESSION_BUS_ADDRESS};
    $self->{name} = lc($class);
    $self->{name} =~ s/.*::(.*?)(?:(?:command|respond|listen|notifi)er)?$/$1/;
    $self->{configfile} = undef;
    bless($self, $class);
    return $self;
}

sub add_options {
    my ($self, $opts) = @_;
    $opts->{'a|address=s'} = \$self->{address};
    $opts->{'c|config=s'} = \$self->{configfile};
    $opts->{'n|name=s'} = \$self->{name};
}

sub handle_options {
    my ($self) = @_;
    die("No configfile specified") unless $self->{configfile};
    die("No such configfile") unless -e $self->{configfile};
    $self->{config} = Config::INI::Reader->read_file($self->{configfile});

    $self->{busname} = $self->{config}{$self->{name}}{busname} || $self->{name};
    unless($self->{busname} =~ /\./) {
        $self->{busname} = 'net.seveas.ubot.helper.' . $self->{busname};
    }
    $self->{busobjname} = '/' . $self->{busname};
    $self->{busobjname} =~ s/\./\//g;

    my $service = Net::DBus->session->export_service($self->{busname});
    # Code copied from Net/Dbus/Object.pm as it insists on creating the object
    # while we don't want that
    $self->{parent} = $service;
    $self->{service} = $service;
    $self->{object_path} = $self->{busobjname};
    $self->{interface} = 'net.seveas.ubot.helper';
    $self->{introspector} = undef;
    $self->{introspected} = 0;
    $self->{callbacks} = {};
    $self->{children} = {};
    $self->get_service->_register_object($self);
    # End of copied code

    $self->{botname} = $self->{config}{$self->{name}}{botname} || 'ubot';
    $self->get_bot;

    my $dbus = Net::DBus->session
        ->get_service('org.freedesktop.DBus')
        ->get_object('/org/freedesktop/DBus')
    or die "Can't get the DBus instance";

    $dbus = $dbus->connect_to_signal('NameOwnerChanged', sub { $self->maybe_get_bot(@_) });
}

sub maybe_get_bot {
    my ($self, $name, $old, $new) = @_;
    $self->get_bot if $name eq "net.seveas.ubot." . $self->{botname};
}

sub get_bot {
    my ($self) = @_;
    $self->{bot} = Net::DBus->session
        ->get_service('net.seveas.ubot.' . $self->{botname})
        ->get_object('/net/seveas/ubot/' . $self->{botname});
    $self->{bot}->register_helper($self->{busname}, $self->{busobjname});
    $self->{bot}->connect_to_signal('message_received', sub { $self->message_received(@_) });
    $self->{bot}->connect_to_signal('message_sent', sub { $self->message_sent(@_) });
    $self->{bot}->connect_to_signal('sync_complete', sub { $self->sync_complete });
    $self->{bot}->connect_to_signal('master_change', sub { $self->{master} = $_[0] });
    $self->{bot}->connect_to_signal('exiting', sub { $self->quit; });
    my $info = $self->{bot}->get_info();
    $self->{synced} = $info->{synced};
    $self->{master} = $info->{master};
    $self->{nickname} = $info->{nickname};
    $self->{channels} = {};
    $self->sync_complete if $self->{synced};
}

sub message_sent {
    my $self = shift;
    my $message = Ubot::Helper::OutMessage->new(@_);
    my $sub = $self->can('out_' . lc($message->{command}));
    $sub->($self, $message) if $sub;
}

sub message_received {
    my $self = shift;
    my $message = Ubot::Helper::InMessage->new(@_);
    $message->{helper} = $self;
    my $sub = $self->can('_in_' . lc($message->{command}));
    $sub->($self, $message) if $sub;
    $sub = $self->can('in_' . lc($message->{command}));
    $sub->($self, $message) if $sub;
}

sub sync_complete {
    my ($self) = @_;
    $self->{synced} = 1;
    foreach my $channel (@{$self->{bot}->get_channels}) {
        $self->{channels}{$channel} = Net::DBus->session
            ->get_service('net.seveas.ubot.' . $self->{botname})
            ->get_object('/net/seveas/ubot/'.$self->{botname}.'/channel/'.escape_object_path($channel));
    }
}
sub escape_object_path {
    my ($path) = @_;
    $path =~ s/([^a-zA-Z0-9])/'_'.ord($1)/eg;
    return $path;
}

sub _in_part {
    my ($self, $message) = @_;
    if($message->{prefix} =~ /^$self->{nickname}!/i) {
        delete $self->{channels}{$message->{target}};
    }
}

sub _in_join {
    my ($self, $message) = @_;
    if($message->{prefix} =~ /^$self->{nickname}!/i) {
        $self->{channels}->{$message->{target}} = Net::DBus->session
            ->get_service('net.seveas.ubot.' . $self->{botname})
            ->get_object('/net/seveas/ubot/'.$self->{botname}.'/channel/'.escape_object_path($message->{target}));
    }
}

sub _in_nick {
    my ($self, $message) = @_;
    if($message->{prefix} =~ /^${self->nickname}!/i) {
        $self->{nickname} = $message->{params}->[0];
    }
}

sub addressed {
    my ($self, $message) = @_;
    return $self->{synced} && $self->{master};
}

sub error {
    my ($self, $msg) = @_;
    $self->{bot}->log($self->{name}, 'ERROR', $msg);
}

sub warning {
    my ($self, $msg) = @_;
    $self->{bot}->log($self->{name}, 'WARNING', $msg);
}

sub info {
    my ($self, $msg) = @_;
    $self->{bot}->log($self->{name}, 'INFO', $msg);
}

sub debug {
    my ($self, $msg) = @_;
    $self->{bot}->log($self->{name}, 'DEBUG', $msg);
}

dbus_method("quit", [], []);
sub quit {
    my ($self) = @_;
    $self->{reactor}->shutdown;
    # Send a GetId to to work around a bug in the reactor
    Net::DBus->session->get_service('org.freedesktop.DBus')->get_object('/org/freedesktop/DBus')->GetId();
}

dbus_method("get_info", [], [["dict", "string", "string"]]);
sub get_info {
    my ($self) = @_;
    return $self->{helper_info};
}

sub run {
    my ($self) = @_;
    my %opts;
    $self->add_options(\%opts);
    GetOptions(%opts);
    $self->handle_options();
    $self->info("helper started");
    $self->{reactor} = Net::DBus::Reactor->main();
    $self->{reactor}->run;
    my $meth = $self->can('exit');
    if($meth) {
        $meth->();
    }
}

# ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

package Ubot::Responder;
use strict;
use warnings;
use vars qw(@ISA);

@Ubot::Responder::ISA = qw(Ubot::Helper);

sub handle_options {
    my ($self) = @_;
    $self->SUPER::handle_options();
    my @channels = split(/,/, $self->{config}{$self->{name}}{'channels'} || '');
    $self->{active_channels} = \@channels;
    $self->{respond_to_all} = 1 if grep { $_ eq 'all' } @{$self->{active_channels}};
    $self->{respond_to_private} = 1 if(grep { $_ eq $self->{name} } @{$self->{active_channels}} || $self->{respond_to_all});
}

sub addressed {
    my ($self, $message) = @_;
    return 0 unless $self->SUPER::addressed($message);
    return 1 if $self->{respond_to_all};
    return 1 if ($self->{respond_to_private} && $message->{target} eq $self->{nickname});
    return 1 if grep { $_ eq $message->{target} } @{$self->{active_channels}};
    return 0;
}

sub send {
    my ($self, $target, $message, $params) = @_;
    if($target =~ /^#/){
        if($params->{action}) {
            $params->{slow} ? $self->{channels}->{$target}->slowdo($message)
                            : $self->{channels}->{$target}->do($message);
        }
        else {
            $params->{slow} ? $self->{channels}->{$target}->slowsay($message)
                            : $self->{channels}->{$target}->say($message);
        }
    }
    else {
        if($params->{action}) {
            $params->{slow} ? $self->{bot}->slowdo($target, $message)
                            : $self->{bot}->do($target, $message);
        }
        else {
            $params->{slow} ? $self->{bot}->slowsay($target, $message)
                            : $self->{bot}->say($target, $message);
        }
    }
}

# ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

package Ubot::Commander;
use strict;
use warnings;
use vars qw(@ISA);

@Ubot::Commander::ISA = qw(Ubot::Responder);

sub handle_options {
    my ($self, $options) = @_;
    $self->SUPER::handle_options($options);
    $self->{prefix} = $self->{config}{$self->{name}}{'prefix'} || '@';
}

sub addressed {
    my ($self, $message) = @_;
    return 0 unless $self->SUPER::addressed($message);
    my $msg = $message->{params}->[0];
    $msg =~ s/^\s*//;
    return 0 unless $msg =~ s/^[$self->{prefix}]\s*//;

    # So, prefix was seen (FIXME: allow nickname as prefix)
    # Now for the commands
    if($self->can('commands')) {
        my $commands = $self->commands;
        my ($c, $a) = split / +/, $msg, 2;
        $a ||= '';
        if(exists($commands->{$c})) {
            $message->{_command} = [$commands->{$c}, $a];
            return 1;
        }
        return 0;
    }
    # If a plugin doesn't define a command list, assume it'll do
    # its own argument handling
    return 1;
}

sub in_privmsg {
    my ($self, $message) = @_;
    if($self->addressed($message)) {
        my ($c, $a) = @{$message->{_command}};
        $c = $self->can($c);
        $c->($self, $message, $a);
    }
}

# ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
package Ubot::Helper::InMessage;
use strict;
use warnings;
use Ubot::rfc2812;

sub new {
    my ($class, $prefix, $command, $target, $params) = @_;
    my $self = {prefix => $prefix, command => $command, params => $params, target => $target};
    if($prefix =~ /^(.*)!(.*)@(.*)$/) {
        $self->{nick} = $1;
        $self->{ident} = $2;
        $self->{host} = $3;
    }
    if(exists($replies{$command})) {
        $self->{ncommand} = $command;
        $command = $self->{command} = $replies{$command};
    }
    bless($self, $class);
    return $self;
}

sub is_ctcp {
    my ($self) = @_;
    return ($self->{command} eq 'PRIVMSG') && ($self->{params}->[-1] =~ /^\x01.*\x01$/);
}

sub is_action {
    my ($self) = @_;
    return ($self->{command} eq 'PRIVMSG') && ($self->{params}->[-1] =~ /^\x01ACTION.*\x01$/);
}
sub reply {
    my ($self, $message, $params) = @_;
    my $target = $params->{private} ? $self->{nick} : $self->{target};
    $self->{helper}->send($target, $message, $params);
}

# ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
package Ubot::Helper::OutMessage;
use strict;
use warnings;

sub new {
    my ($class, $command, $params) = @_;
    my $self = {command => $command, params => $params};
    bless($self, $class);
    return $self;
}

1;
