# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 14:09:40
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-05 14:27:09
# --------------------------------------------

VIEW_CLASS_SETTINGS = {
    "TemplateView": {
        "queries": [
            {
                "question": "Any comment you want to add to the view?",
                "key": "comment",
                'required': False
            }
        ],
        "append": "View"
    },
    "ListView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app_label)s/%(model)s_list.html",
                'attr_type':"str",
                'required': True
            }
        ],
        "append": "ListView"
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
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app_label)s/%(model_name)s_detail.html",
                'attr_type':"str",
                'required': True
            }
        ],
        "append": "DetailView"
    },
    "FormView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "",
                "key": "form_class",
                'required': True
            },
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app)s/%(model)s_form.html",
                'attr_type':"str",
                'required': True
            }
        ]},
    "RedirectView": {}
}


IGNORE_MODULES = ["django.views.i18n", "django.contrib.admin.views"]