import random
import string

from django.contrib.auth import get_user_model
from django.urls import reverse


def create_test_user(unique=False):
    password = 'password'
    if unique:
        username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    else:
        username = 'Alibaba'
    return get_user_model().objects.create_user(username=username, password=password), password


def testserver_reverse(*args, **kwargs):
    """
    Prepend to reverse() prefix "http://testserver" which is default domain (+protocol) used by Django test Client.
    """
    return 'http://testserver%s' % reverse(*args, **kwargs)
