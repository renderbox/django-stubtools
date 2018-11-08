# 0 HERE ARE SOME COMMENTS
from django.conf.urls import url
# 2
from . import views
# 4
urlpatterns = [
    url(r'^profile/$', views.ProfileView.as_view(), name='poop-profile'),
    url(r'^profile_too/$', views.ProfileTooView.as_view(), name='poop-too-profile'),
]
# 9