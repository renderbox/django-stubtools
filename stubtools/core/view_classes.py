# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 14:09:40
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 17:41:00
# --------------------------------------------

VIEW_CLASS_DEFAULT_SETTINGS = {
    "queries": [
        {
            "question": "What should the created template be called?",
            "key": "template_name",
            "default": "%(app_label)s/%(view_name)s.html",
            'attr_type':"str",
            'required': True
        },
        {
            "question": "What do you want the Resource Name to be?",
            "key": "resource_name",
            "default": "%(app_label)s-%(view_name)s",
            "as_atttr": False,
        },
        {
            "question": "What do you want the Resource URL Pattern to be?",
            "key": "resource_pattern",
            "default": "%(view_name)s/",
            "as_atttr": False,
        },
    ],
    "view_suffix": "View",
    "template": 'views/TemplateView.html.j2',
}


VIEW_CLASS_SETTINGS = {
    "django.views.generic.base.TemplateView": {
        "queries": [],
        "view_suffix": "View",
        "class_name": "TemplateView",
        "module": "django.views.generic",
        "default_values":
            {
                "template_name": "%(app_label)s/%(view_name)s.html",
                "resource_name": "%(app_label)s-%(view_name)s",
                "resource_pattern": "%(view_name)s/",
            },
    },
    "django.views.generic.list.ListView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Did you want to add a queryset?",
                "key": "queryset",
                "default": "%(model)s.objects.all()",
                'required': True
            },
            {
                "question": "What variable name should be used for the model instances in the template?",
                "key": "template_objects_name",
                'required': False,
                "default": "object_list",
                "ignore_default": True,
            },
        ],
        "class_name": "ListView",
        "view_suffix": "ListView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_list.html",
                "resource_name": "%(app_label)s-%(view_name)s-%(model_name)s-list",
                "resource_pattern": "%(model_name)s/list/",
            },
        "template": 'views/ListView.html.j2',
    },
    "django.views.generic.detail.DetailView": {
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
        ],
        "class_name": "DetailView",
        "view_suffix": "DetailView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_detail.html",
                "resource_name": "%(app_label)s-%(view_name)s-detail",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/detail/",
            },
    },
    "django.views.generic.edit.CreateView": {
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
        "template": 'views/CreateView.html.j2',
        "view_suffix": "CreateView",
        "class_name": "CreateView",

        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_form.html",
                "resource_name": "%(app_label)s-%(view_name)s-create",
                "resource_pattern": "%(view_name)s/%(model_name)s/create/",
            }
    },
    "django.views.generic.edit.UpdateView": {
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
                "question": "Which Form do you want to use?",
                "key": "form_class",
                'required': True,
                "default": "%(model)sForm",
            },
        ],
        "view_suffix": "UpdateView",
        "class_name": "UpdateView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_form.html",
                "resource_name": "%(app_label)s-%(view_name)s-update",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/edit/",
            },
        "template": 'views/UpdateView.html.j2',
    },
    "django.views.generic.edit.DeleteView": {
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
                "question": "Which Form do you want to use?",
                "key": "form_class",
                'required': True,
                "default": "%(model)sForm",
            },
        ],
        "view_suffix": "DeleteView",
        "class_name": "DeleteView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_confirm_delete.html",
                "resource_name": "%(app_label)s-%(view_name)s-delete",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/delete/",
            },
        "template": 'views/DeleteView.html.j2',
    },
    "django.views.generic.edit.FormView": {
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
        "view_suffix": "FormView",
        "class_name": "FormView",
        "default_values":
            {
                "template_name": "%(app_label)s/%(model_name)s_form.html",
                "resource_name": "%(app_label)s-%(view_name)s-form",
                "resource_pattern": "%(view_name)s/<slug:%(slug_url_kwarg)s>/edit/",
            }
        },
    "django.views.generic.base.RedirectView": {
        "view_suffix": "RedirectView",
        "class_name": "RedirectView",
        }
    }

STUBTOOLS_IGNORE_MODULES = ["django.views.i18n", "django.contrib.admin.views"]
