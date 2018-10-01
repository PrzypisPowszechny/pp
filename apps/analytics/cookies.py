from datetime import timedelta

from django.utils import timezone

IAMSTAFF_COOKIE = 'pp_iamstaff'


def iamstaff_set_cookie():
    return {'key': IAMSTAFF_COOKIE, 'value': '1', 'expires': timezone.now() + timedelta(days=365 * 10)}


def is_iamstaff(request):
    return request.COOKIES.get(IAMSTAFF_COOKIE) is not None
