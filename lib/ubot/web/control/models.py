from django.db import models
from django.contrib.auth.models import User, Group

class Bot(models.Model):
    name = models.CharField("D-Bus name", max_length=32, unique=True)

    def has_access(self, user, permission):
        return permission in self.get_access(user) # or user.is_superuser

    def get_access(self, user):
        try:
            return UserBotPermissions.objects.get(bot=self, user=user).permissions.values_list('name', flat=True)
        except UserBotPermissions.DoesNotExist:
            return []

    def __unicode__(self):
        return self.name

class BotPermission(models.Model):
    name = models.CharField("Permission", max_length=20, unique=True)
    description = models.CharField("Description", max_length=60)

    def __unicode__(self):
        return self.description

class UserBotPermissions(models.Model):
    bot = models.ForeignKey(Bot)
    user = models.ForeignKey(User)
    permissions = models.ManyToManyField(BotPermission)

    def __unicode__(self):
        return u"Permissions for %s" % self.user.get_full_name()

class PrefixMaskManager(models.Manager):
    def user_for_prefix(self, prefix):
        return self.users_for_prefix(prefix).get()

    def users_for_prefix(self, prefix):
        masks = self.extra(where=["%s REGEXP(mask)"], params=[prefix])
        return User.objects.filter(prefixmask__in=masks).distinct()

class PrefixMask(models.Model):
    user = models.ForeignKey(User)
    mask = models.CharField("Prefix mask", max_length=64,
            help_text="Example: .*!.*@ubuntu/member/seveas")

    objects = PrefixMaskManager()

    def save(self, *args, **kwargs):
        if not self.mask.startswith('^'):
            self.mask = '^' + self.mask
        if not self.mask.endswith('$'):
            self.mask += '$'
        return super(PrefixMask, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s|%s" % (self.user.username, self.mask)
