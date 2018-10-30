from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/$', views.ProfileView.as_view(), name='poop-profile'),
)
]
