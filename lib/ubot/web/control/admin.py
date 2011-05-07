from django.contrib import admin
from ubot.web.control.models import Bot

class BotAdmin(admin.ModelAdmin):
    fields = ('name', 'controllers', 'controller_groups')
    readonly_fields = ('name',)
    add_form_template = 'ubot/control/no_adding.html'

admin.site.register(Bot, BotAdmin)
