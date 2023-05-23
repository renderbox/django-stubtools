# LOAD DEFAULT stubtools SETTINGS

from django.conf import settings


def template_loader_check():
    for item in settings.TEMPLATES:
        if item['BACKEND'] = 'django.template.backends.django.DjangoTemplates':
            return

    print('''

    Make sure to add the following to your settings.py under 'TEMPLATES':

    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'environment': 'stubtools.jinja2.environment',
        }
    }
    ''')

    # settings.TEMPLATES.append(cfg)



template_loader_check()