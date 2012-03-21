# These is a full urlconf to be used by the instaweb helper

from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Redirect '/' to the control interface
    (r'^$', lambda request: HttpResponseRedirect('control/')),

    # Authentication
    (r'^login/', 'django.contrib.auth.views.login'),
    (r'^logout/', 'django.contrib.auth.views.logout', {'next_page': "/"}),

    # Django admin documentation
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Django admin
    (r'^admin/', include(admin.site.urls)),

    # Ubot control interface
    (r'^control/', include('ubot.web.control.urls')),

    (r'^media/ubot/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
