import re
from datetime import timedelta
from logging import getLogger

from django.utils import timezone

CID_PARAM = 'ga_cookie'
GID_PARAM = 'gid_cookie'
CID_COOKIE = '_ga'
GID_COOKIE = '_gid'

# Example of cid cookie: "GA1.2-2.2096600588.1532966673". The "2-2" part is optional or may be just "2".
# Only "2096600588.1532966673" is interesting for us.
cid_regex = r'^GA\d\.(?:\d+(?:\-\d+)?\.)?(?P<cid>\d+\.\d+)$'

logger = getLogger('pp.analytics')


def set_cookies(request_data):
    # Limit the length but beside that accept any value (this is just cookie used as local id)
    cid = request_data.get(CID_PARAM)[:64]
    gid = request_data.get(GID_PARAM)[:64]
    cookie_base = {'expires': timezone.now() + timedelta(days=360*100), 'httponly': False}
    cookies = []
    if cid:
        cookies.append(dict(key=CID_COOKIE, value=cid, **cookie_base))
    if gid:
        cookies.append(dict(key=GID_COOKIE, value=gid, **cookie_base))
    return cookies


def read_cid_from_cookie(request):
    cookie_val = request.COOKIES.get(CID_COOKIE, '')
    match = re.match(cid_regex, cookie_val)
    if not match:
        return None
    return match.group('cid')
