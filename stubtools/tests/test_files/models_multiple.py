# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-26 18:03:40
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-14 17:57:08
# --------------------------------------------
from django.db import models

from django.utils.translation import ugettext_lazy as _     # For localization


class User(models.Model):
    name = models.CharField(_("Name"), max_length=300 )


class Car(models.Model):
    name = models.CharField(_("Name"), max_length=300 )


class House(models.Model):
    name = models.CharField(_("Name"), max_length=300 )
    address = models.CharField(_("Name"), max_length=300 )
