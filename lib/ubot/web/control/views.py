from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ubot.web.control.models import Bot
import ConfigParser
import dbus
import functools
import os
import re
import simplejson
import ubot.irc
import ubot.util

class HttpResponseUnavailable(HttpResponse):
    status_code = 503

class JsonResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        super(JsonResponse, self).__init__(simplejson.dumps(content, sort_keys=True), *args, **kwargs)

def control_method(meth):
    @functools.wraps(meth)
    def wrapper(request, *args, **kwargs):
        if 'bot' in kwargs:
            bot = get_object_or_404(Bot,name=kwargs['bot'])
            if not bot.has_access(request.user, 'webadmin'):
                return HttpResponseForbidden("No access")

        try:
            dbus.SessionBus()
        except:
            return HttpResponseServerError("The dbus daemon at %s is not running or not accessible. Start dbus and retry." % os.environ['DBUS_SESSION_BUS_ADDRESS'])

        if 'bot' in kwargs:
            bus = dbus.SessionBus().get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
            try:
                bus.GetNameOwner('net.seveas.ubot.' + kwargs['bot'])
            except dbus.DBusException, e:
                if e.get_dbus_name() == 'org.freedesktop.DBus.Error.NameHasNoOwner':
                    return HttpResponseUnavailable("The bot named %s is not running. Start the bot and retry." % kwargs['bot'])
                else:
                    raise

        # Replace 'channel' with a channel object
        if 'channel' in kwargs:
            kwargs['channel'] = dbus.SessionBus().get_object('net.seveas.ubot.' + kwargs['bot'],
                    '/net/seveas/ubot/%s/channel/%s' % (kwargs['bot'], ubot.util.escape_object_path(kwargs['channel'])))
        # Replace 'bot' with a bot object
        if 'bot' in kwargs:
            kwargs['bot'] = dbus.SessionBus().get_object('net.seveas.ubot.' + kwargs['bot'],
                                                     '/net/seveas/ubot/' + kwargs['bot'])

        # Find all required arguments
        if hasattr(meth, 'im_func'):
            code = meth.im_func.__code__
            defaults = meth.im_func.func_defaults
            varnames = code.co_varnames[1:code.co_argcount]
        else:
            code = meth.__code__
            defaults = meth.func_defaults
            varnames = code.co_varnames[:code.co_argcount]
        if defaults:
            defaults = dict(zip(code.co_varnames[:code.co_argcount][-len(defaults):], defaults))
        else:
            defaults = {}
        for var in varnames:
            if var in ('request', 'bot', 'helper', 'botname'):
                continue
            if var == 'channel' and code.co_name != 'join':
                continue
            if var not in request.POST and var not in defaults:
                return HttpResponseBadRequest()
            if var in request.POST:
                kwargs[var] = request.POST[var]
        result = {'status': 'ok', 'error': ''}
        try:
            result.update(meth(request, *args, **kwargs) or {})
        except Exception, e:
            result = {'status': 'error', 'error': str(e)}
        return JsonResponse(result, content_type = request.is_ajax() and 'application/json' or 'text/plain')

    return wrapper

@login_required
def index(request):
    # Create bot objects for live or activatable bots
    try:
        bus = dbus.SessionBus()
    except:
        return HttpResponseServerError("The dbus daemon at %s is not running or not accessible. Start dbus and retry." % os.environ['DBUS_SESSION_BUS_ADDRESS'])
    bus = bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus')
    active = bus.ListNames()
    for name in bus.ListActivatableNames() + active:
        m = re.match(r'^net\.seveas\.ubot\.([a-zA-Z0-9_]+)$', name)
        if m:
            Bot.objects.get_or_create(name=m.group(1))
    bots = list(Bot.objects.all())
    for b in bots:
        b.active = ('net.seveas.ubot.' + b.name) in active
        b.state = ['off','on'][b.active]
    ctx = RequestContext(request, {'bots': bots})
    return render_to_response('ubot/control/index.html', context_instance=ctx)

def bot(request, bot):
    bot = get_object_or_404(Bot, name=bot)
    if not bot.has_access(request.user, 'webadmin'):
        return HttpResponseForbidden("No access")
    ctx = RequestContext(request, {'bot': bot})
    return render_to_response('ubot/control/bot.html', context_instance=ctx)

@control_method
def start_bot(request, botname):
    try:
        bus = dbus.SessionBus().get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
        bus.StartServiceByName('net.seveas.ubot.' + botname, dbus.types.UInt32(0))
    except:
        # Ignore errors, retries will be attempted
        pass

@control_method
def channels(request, bot):
    return {'channels': bot.get_channels()}

@control_method
def info(request, bot):
    return bot.get_info()

@control_method
def join(request, bot, channel):
    bot.join(channel)

@control_method
def nick(request, bot, nick):
    bot.nick(nick)

@control_method
def quit(request, bot, message):
    bot.quit(message)

@control_method
def do(request, bot, target, message):
    bot.do(target, message)

@control_method
def say(request, bot, target, message):
    bot.say(target, message)

@control_method
def raw(request, bot):
    pass

@control_method
def helpers(request, bot):
    blacklisted_names = ('org.freedesktop.DBus', bot.requested_bus_name)
    bus = dbus.SessionBus().get_object('org.freedesktop.DBus','/org/freedesktop/DBus')
    helpers = dict([(x, False) for x in bus.ListActivatableNames() if x not in blacklisted_names])
    helpers.update(dict(bot.get_helpers()))
    return {'helpers': sorted(helpers.items())}

@control_method
def stop_helper(request, bot, helper):
    helpers = dict(bot.get_helpers())
    if helper not in helpers:
        raise ValueError("No such helper")
    helper = dbus.SessionBus().get_object(helper, helpers[helper])
    helper.quit(dbus_interface='net.seveas.ubot.helper')

@control_method
def start_helper(request, bot, helper):
    blacklisted_names = ('org.freedesktop.DBus', bot.requested_bus_name)
    bus = dbus.SessionBus().get_object('org.freedesktop.DBus','/org/freedesktop/DBus')
    helpers = dict([(x, False) for x in bus.ListActivatableNames() if x not in blacklisted_names])
    helpers.update(dict(bot.get_helpers()))
    if helpers.get(helper, None):
        raise ValueError("Helper %s already running" % helper)
    if helper not in helpers:
        raise ValueError("Helper %s cannot be autostarted" % helper)
    bus.StartServiceByName(helper, dbus.types.UInt32(0))

@control_method
def helper_info(request, bot, helper):
    helpers = dict(bot.get_helpers())
    if helper not in helpers:
        return {'running': False, 'info': {}}
    helper = dbus.SessionBus().get_object(helper, helpers[helper])
    info = helper.get_info(dbus_interface='net.seveas.ubot.helper')
    return {'running': True, 'info': info}

@control_method
def channel_do(request, bot, channel, message):
    channel.do(message)

@control_method
def channel_say(request, bot, channel, message):
    channel.say(message)

@control_method
def channel_part(request, bot, channel, message):
    channel.part(message)

@control_method
def channel_topic(request, bot, channel, topic=None):
    if topic:
        channel.set_topic(topic)
    else:
        return {'topic': channel.get_topic()}

@control_method
def channel_mode(request, bot, channel, mode=None):
    if mode:
        channel.set_mode(mode)
    else:
        return {'mode': channel.get_mode()}

@control_method
def channel_nicks(request, bot, channel):
    n = dict([(ubot.irc.IrcString(nick), mode) for nick, mode in channel.get_nicks().items()])
    return {'nicks': n, 'count': len(n.keys())}

@control_method
def channel_invite(request, bot, channel, nick):
    channel.invite(nick)

@control_method
def channel_kick(request, bot, nick, message):
    channel.kick(nick, message)
