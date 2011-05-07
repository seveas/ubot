from django.conf.urls.defaults import *

urlpatterns = patterns('ubot.web.control.views',
    (r'^$', 'index'),

    (r'^rest/(?P<botname>[A-Za-z0-9]+)/start/$', 'start_bot'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channels/$', 'channels'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/info/$', 'info'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/join/$', 'join'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/nick/$', 'nick'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/quit/$', 'quit'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/do/$', 'do'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/say/$', 'say'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/raw/$', 'raw'),

    (r'^rest/(?P<bot>[A-Za-z0-9]+)/helpers/$', 'helpers'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/helper/(?P<helper>[a-zA-Z.0-9]+)/$', 'helper_info'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/helper/(?P<helper>[a-zA-Z.0-9]+)/stop/$', 'stop_helper'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/helper/(?P<helper>[a-zA-Z.0-9]+)/start/$', 'start_helper'),

    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/do/$', 'channel_do'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/say/$', 'channel_say'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/part/$', 'channel_part'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/topic/$', 'channel_topic'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/mode/$', 'channel_mode'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/nicks/$', 'channel_nicks'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/invite/$', 'channel_invite'),
    (r'^rest/(?P<bot>[A-Za-z0-9]+)/channel/(?P<channel>[^/]+)/kick/$', 'channel_kick'),

    (r'^(?P<bot>[a-zA-Z0-9_]+)/$', 'bot'),
)
