from urllib.parse import urlencode, parse_qsl, urlsplit

OMITTED_QUERY_VARS = (
    # Universal Tracking Module convention names
    'utm_campaign',
    'utm_medium',
    'utm_term',
    'utm_name',
    'utm_source',
    # General convention for references
    'ref',
)


def standardize_url_id(data):
    """
    Format url in the way that:
      - ignores protocol
      - ignores fragment(anchor)
      - ignores some blacklisted query vars like utm etc
      - set '/' as a path if none given
      - removes '?' if no query string
    """
    if not data:
        return ''
    url_parsed = urlsplit(data)
    query_tuples = parse_qsl(url_parsed.query)
    new_query_tuples = []
    for var_name, val in query_tuples:
        if var_name not in OMITTED_QUERY_VARS:
            new_query_tuples.append((var_name, val))
    return '{netloc}{path}{query}'.format(
        netloc=url_parsed.netloc,
        path=url_parsed.path if url_parsed.path else '/',
        query='?' + urlencode(new_query_tuples) if new_query_tuples else ''
    )


def standardize_url(data):
    """
        Format url in the way that:
          - ignores fragment(anchor)
          - ignores some blacklisted query vars like utm etc
          - set '/' as a path if none given
          - removes '?' if no query string
    """
    if not data:
        return ''
    url_parsed = urlsplit(data)
    query_tuples = parse_qsl(url_parsed.query)
    new_query_tuples = []
    for var_name, val in query_tuples:
        if var_name not in OMITTED_QUERY_VARS:
            new_query_tuples.append((var_name, val))
    return '{scheme}{netloc}{path}{query}'.format(
        scheme=url_parsed.scheme + '://' if url_parsed.scheme else '',
        netloc=url_parsed.netloc,
        path=url_parsed.path if url_parsed.path else '/',
        query='?' + urlencode(new_query_tuples) if new_query_tuples else ''
    )
