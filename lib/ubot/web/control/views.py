from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
import dbus
import functools
import os
import simplejson
import ubot.util

class JsonResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        super(JsonResponse, self).__init__(simplejson.dumps(content), *args, **kwargs)

def control_method(meth):
    @functools.wraps(meth)
    def wrapper(request, *args, **kwargs):
        # Check authentication
        if not request.user.has_perm('ubot_control'):
            return HttpResponseForbidden("No access")

        try:
            dbus.SessionBus()
        except:
            return HttpResponseServerError("The dbus daemon at %s is not running or not accessible. Start dbus and retry." % os.environ['DBUS_SESSION_BUS_ADDRESS'])

        bus = dbus.SessionBus().get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
        try:
            bus.GetNameOwner('net.seveas.ubot.' + kwargs['bot'])
        except dbus.DBusException, e:
            if e.get_dbus_name() == 'org.freedesktop.DBus.Error.NameHasNoOwner':
                return HttpResponseServerError("The bot named %s is not running. Start the bot and retry." % kwargs['bot'])
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
            if var in ('request', 'bot'):
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

@user_passes_test(lambda user: user.has_perm('ubot_control'))
def index(request):
    ctx = RequestContext(request, {'UBOT_BOTNAME': settings.UBOT_BOTNAME})
    return render_to_response('ubot/control/index.html', context_instance=ctx)

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
def channel_do(request, bot, channel, message):
    channel.do(message)

@control_method
def channel_say(request, bot, channel, message):
    channel.do(message)

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
    return {'nicks': channel.get_nicks()}

@control_method
def channel_invite(request, bot, channel, nick):
    channel.invite(nick)

@control_method
def channel_kick(request, bot, nick, message):
    channel.kick(nick, message)
