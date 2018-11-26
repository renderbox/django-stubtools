from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(models.Model):
    name = models.CharField(_("Name"), max_length=300 )


class Something(models.Model):
    name = models.CharField(_("Name"), max_length=300 )
