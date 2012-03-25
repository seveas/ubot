from django.db import models

class Factoid(models.Model):
    name = models.CharField("Name", max_length=25, db_index=True)
    value = models.TextField("Value", max_length=1024)
    alias_of = models.ForeignKey('self', verbose_name = "Alias of", blank=True, null=True)
    channel = models.CharField("Channel", blank=True, max_length=30, db_index=True, help_text="Leave blank to make it default")
    added_by = models.CharField("Author", max_length=50, editable=False)
    added_at = models.DateTimeField("Added at", auto_now=True)
    popularity = models.IntegerField("Popularity", default=0, editable=False)

    error = False

    def __unicode__(self):
        if self.channel:
            return u'%s (%s)' % (self.name, self.channel)
        return self.name

    def msg(self):
        if self.value.startswith('<reply>'):
            return self.value[7:].lstrip()
        else:
            return '%s is %s' % (self.name, self.value)

    class Meta:
        unique_together = (('name','channel'),)

debian = ('lenny','squeeze','wheezy','sid')
ubuntu = ('maverick','natty','oneiric','precise')
releases = [(x,x) for x in debian + ubuntu]
class SourcePackage(models.Model):
    name = models.CharField("Name", max_length=64, db_index=True)
    version = models.CharField("Version", max_length=64)
    release = models.CharField("Release", max_length=16, db_index=True, choices=releases)

    error = False
    alias_of = None

    def url(self):
        if self.release in debian:
            return 'http://packages.qa.debian.org/%s/%s.html' % (self.name[0], self.name)
        elif self.release in ubuntu:
            return 'https://launchpad.net/ubuntu/+source/' + self.name
        return ''

    def msg(self):
        return "%s is a sourcepackage in %s, version %s %s" % (self.name, self.release, self.version, self.url())

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.name, self.version, self.release)

class BinaryPackage(models.Model):
    name = models.CharField("Name", max_length=64, db_index=True)
    version = models.CharField("Version", max_length=64)
    release = models.CharField("Release", max_length=16, db_index=True, choices=releases)
    shortdesc = models.CharField("Name", max_length=128)
    source = models.CharField("Source", max_length=64, blank=True, db_index=True)
    component = models.CharField("Component", max_length=32)
    priority = models.CharField("Priority", max_length=16)

    error = False
    alias_of = None

    def url(self):
        if self.release in debian:
            s = self.source or self.name
            return 'http://packages.qa.debian.org/%s/%s.html' % (s[0], s)
        elif self.release in ubuntu:
            s = self.source or self.name
            return 'https://launchpad.net/ubuntu/+source/' + s
        return ''

    def msg(self):
        source = self.source and (' (Source: %s)' % self.source) or ''
        return "%s%s: %s. In component %s, is %s. Version %s (%s) %s" % (self.name, source, self.shortdesc, self.component,
                                                                        self.priority, self.version, self.release, self.url())

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.name, self.version, self.release)
