from django.contrib import admin
# 2
from .models import User, Something


###############
# MODEL ADMINS
###############

class UserAdmin(admin.ModelAdmin):
    pass


class SomethingAdmin(admin.ModelAdmin):
    pass



###############
# REGISTRATION
###############

admin.site.register(User, UserAdmin)
admin.site.register(Something, SomethingAdmin)
