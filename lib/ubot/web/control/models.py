from django.db import models
from django.contrib.auth.models import User, Group

class Bot(models.Model):
    name = models.CharField("D-Bus name", max_length=32)
    controllers = models.ManyToManyField(User, verbose_name="People who can control the bot")
    controller_groups = models.ManyToManyField(Group, verbose_name="Groups who can control the bot")
