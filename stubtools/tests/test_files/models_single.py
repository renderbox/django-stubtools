# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-26 18:03:29
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-26 18:04:09
# --------------------------------------------
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(models.Model):
    name = models.CharField(_("Name"), max_length=300 )
