# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 14:09:40
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-08 11:18:25
# --------------------------------------------


VIEW_CLASS_DEFAULT_SETTINGS = {
    "queries": [
        {
            "question": "Which template to use?",
            "key": "template_name",
            "default": "%(app_label)s/%(view_name)s.html",
            'attr_type':"str",
            'required': True
        },
        {
            "question": "What do you want the Path Name to be?",
            "key": "resource_name",
            "default": "%(app_label)s-%(view_name)s",
            "as_atttr": False,
        },
        {
            "question": "What do you want the Resource Pattern to be in the view?",
            "key": "resource_pattern",
            "default": "%(view_name)s/",
            "as_atttr": False,
        },
    ],
    "append": "View",
    "template": 'views/TemplateView.html.j2',
}


VIEW_CLASS_SETTINGS = {
    "TemplateView": {
        "queries": [],
        "append": "View",
        "module": "django.views.generic",
        "default_values":
            {
                "template_name": "%(app_label)s/%(view_name)s.html",
                "resource_name": "%(app_label)s-%(view_name)s",
                "resource_pattern": "%(view_name)s/",
            },
    },
    "ListView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
        ],
        "append": "ListView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_list.html",
                "resource_name": "%(app_label)s-%(view_name)s",
                "resource_pattern": "%(view_name)s/%(model_name)s/list/",
            },
        "template": 'views/ListView.html.j2',
    },
    "DetailView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Slug Field in the Resource Path?",
                "key": "slug_url_kwarg",
                'required': False,
                "default": "slug",
                "ignore_default": True,
            },
            {
                "question": "What variable name should be used for the model instance in the template?",
                "key": "template_object_name",
                'required': False,
                "default": "object",
                "ignore_default": True,
            },
            {
                "question": "Which Form do you want to use?",
                "key": "form_class",
                'required': True,
                "default": "%(model)sForm",
            },
        ],
        "append": "DetailView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_detail.html",
                "resource_name": "%(app_label)s-%(view_name)s",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/details/",
            },
    },
    "FormView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Which Form do you want to use?",
                "key": "form_class",
                'required': True,
                "default": "%(model)sForm",
            },
        ],
        "append": "FormView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_form.html",
                "resource_name": "%(app_label)s-%(view_name)s",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/details/",
            },
        },
    "RedirectView": {}
}

STUBTOOLS_IGNORE_MODULES = ["django.views.i18n", "django.contrib.admin.views"]