from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils import translation
from jinja2 import Environment, Markup


def csrf_field(csrf_token):
    return Markup(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">'.format(
            csrf_token=csrf_token
        )
    )


def environment(**kwargs):
    added_extensions = [
        'sass_processor.jinja2.ext.SassSrc',
        'compressor.contrib.jinja2ext.CompressorExtension',
        'jinja2.ext.loopcontrols'
    ]
    if 'extensions' not in kwargs:
        kwargs['extensions'] = added_extensions
    else:
        kwargs['extensions'].update(
            added_extensions
        )

    env = Environment(**kwargs)
    env.globals.update(
        {
            'static': staticfiles_storage.url,
            'url': reverse,
            'lang_code': translation.get_language(),
            'GOOGLE_WEB_CREDENTIALS': settings.GOOGLE_WEB_CREDENTIALS,
            'csrf_field': csrf_field
        }
    )
    if settings.DEBUG:
        env.globals.update(
            {
                'dir': dir
            }
        )
    return env
