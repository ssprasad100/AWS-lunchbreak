from __future__ import absolute_import

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils import translation
from jinja2 import Environment


def environment(**kwargs):
    extensions = [] if 'extensions' not in kwargs else kwargs['extensions']
    extensions.append('sass_processor.jinja2.ext.SassSrc')
    kwargs['extensions'] = extensions

    env = Environment(**kwargs)
    env.globals.update(
        {
            'static': staticfiles_storage.url,
            'url': reverse,
            'lang_code': translation.get_language(),
        }
    )
    return env
