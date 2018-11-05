# 0 HERE ARE SOME COMMENTS
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.generic.list import ListView
# 3
# Create your views here.
##--------
## Profile
# 7
class ProfileView(TemplateView):
    template_name = 'poop/profile.html'
# 10
# 11 POST PROFILE VIEW
# 12