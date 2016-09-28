from django.core.urlresolvers import reverse
from django.utils.http import urlencode


def url_query(name, **kwargs):
    return '{location}?{query}'.format(
        location=reverse(name),
        query=urlencode(kwargs)
    )
