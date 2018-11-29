# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-28 10:41:16
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-28 14:53:19
# --------------------------------------------
from django.contrib import admin
from .models import Content, Product, Category


###############
# ACTIONS
###############


###############
# INLINES
###############

# class ReleaseInline(admin.TabularInline):
#     model = Release
#     extra = 1


###############
# ADMINS
###############

class ContentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled']
    inlines = [ReleaseInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled']

###############
# REGISTRATION
###############

admin.site.register(Category)
admin.site.register(Content, ContentAdmin)
admin.site.register(Product, ProductAdmin)
