from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.
##--------
## Profile

class ProfileView(TemplateView):
    template_name = 'poop/profile.html'


