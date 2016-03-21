from __future__ import absolute_import

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils import translation
from jinja2 import Environment


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
            'lang_code': translation.get_language()
        }
    )
    return env
