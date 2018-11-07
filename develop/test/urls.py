# 0 HERE ARE SOME COMMENTS
from django.conf.urls import url
from . import views
# 3
urlpatterns = [
    url(r'^profile/$', views.ProfileView.as_view(), name='poop-profile'),
]
# 7