# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-28 15:09:49
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-28 15:09:59
# --------------------------------------------
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^profile/$', views.ProfileView.as_view(), name='poop-profile'),
    url(r'^profile_too/$', views.ProfileTooView.as_view(), name='poop-too-profile'),
]
