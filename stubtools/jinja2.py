# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-09 12:44:27
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-09 12:52:41
# --------------------------------------------
# from django.templatetags.static import static
# from django.urls import reverse

from jinja2 import Environment

def environment(**options):
    options['autoescape'] = False
    env = Environment(**options)
    print(env)
    # env.globals.update({
    #     'static': static,
    #     'url': reverse,
    # })
    return env
