from django.db import models
from django.contrib.auth.models import User, Group

class Bot(models.Model):
    name = models.CharField("D-Bus name", max_length=32, unique=True)
    controllers = models.ManyToManyField(User, verbose_name="People who can control the bot", blank=True)
    controller_groups = models.ManyToManyField(Group, verbose_name="Groups who can control the bot", blank=True)

    def has_access(self, user):
        if not user or user.is_anonymous():
            return False
        return False \
           or user.id in self.controllers.values_list('id',flat=True) \
           or set(user.groups.values_list('id', flat=True)).intersection(set(self.controller_groups.values_list('id', flat=True)))

    def __unicode__(self):
        return self.name
