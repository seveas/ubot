from django.contrib import admin
from django import forms
from ubot.web.control.models import Bot, PrefixMask, UserBotPermissions, BotPermission
import re

class UserBotPermissionsInline(admin.TabularInline):
    model = UserBotPermissions
    verbose_name = "Permission set"
    verbose_name_plural = "Permission sets"
    extra = 0

class BotAdmin(admin.ModelAdmin):
    fields = ('name',)
    readonly_fields = ('name',)
    add_form_template = 'ubot/control/no_adding.html'
    inlines = [UserBotPermissionsInline]
admin.site.register(Bot, BotAdmin)

class PrefixMaskForm(forms.ModelForm):
    def clean_prefixmask(self):
        mask = self.cleaned_data['mask']
        try:
            re.compile(mask)
        except re.error, e:
            raise Forms.ValidationError("Invalid regexp for prefix: %s" % str(e))
        return mask

    class Meta:
        model = PrefixMask

class PrefixMaskAdmin(admin.ModelAdmin):
    fields = ('user', 'mask')
    search_fields = ('user', 'mask')
    list_display = ('user', 'mask')
    form = PrefixMaskForm
admin.site.register(PrefixMask, PrefixMaskAdmin)

BotPermission.objects.get_or_create(name="webadmin", description="Control the bot via the web interface")
