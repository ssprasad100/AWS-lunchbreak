from django.core.urlresolvers import reverse
from django.utils.http import urlencode


def url_query(name, kwargs=None, **query):
    if isinstance(kwargs, dict):
        query.update(kwargs)
    return '{location}?{query}'.format(
        location=reverse(name),
        query=urlencode(query)
    )
