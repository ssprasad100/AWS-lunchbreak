from django.core.urlresolvers import reverse
from django.utils.http import urlencode


def url_query(name, reverse_kwargs=None, kwargs=None, **query):
    if isinstance(kwargs, dict):
        query.update(kwargs)
    if reverse_kwargs is None:
        reverse_kwargs = {}

    return '{location}?{query}'.format(
        location=reverse(name, kwargs=reverse_kwargs),
        query=urlencode(query)
    )
