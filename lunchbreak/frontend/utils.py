from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


def add_query_params(url, **params):
    """Add query parameters to a given URL and return the modified url.

    >>> add_query_params('http://example.com?foo=bar', foo='stuff', bar='bar')
    'http://example.com?foo=stuff&bar=bar'
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params.update(params)

    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))
