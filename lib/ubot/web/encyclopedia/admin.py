from ubot.web.encyclopedia.models import *
from django.contrib import admin

class FactoidAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'added_by', 'value', 'alias_of')
    search_fields = ('name', 'value')
    ordering = ('name',)
admin.site.register(Factoid, FactoidAdmin)

class SourcePackageAdmin(admin.ModelAdmin):
    search_fields = ('packagename',)
    list_filter = ('release',)
    list_display = ('packagename','release','version')
admin.site.register(SourcePackage, SourcePackageAdmin)

class BinaryPackageAdmin(admin.ModelAdmin):
    search_fields = ('packagename','source')
    list_filter = ('release','component')
    list_display = ('packagename','source','release','version','component')
admin.site.register(BinaryPackage, BinaryPackageAdmin)
