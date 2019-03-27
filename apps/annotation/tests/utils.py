import string

import random
from deepmerge import Merger
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


def create_test_user(unique=False, use_id=None):
    password = 'password'
    if unique:
        username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    else:
        username = 'Alibaba'
    return get_user_model().objects.create_user(username=username, password=password), password


def get_or_create_user(pk):
    User: AbstractUser = get_user_model()
    user = User.objects.filter(id=pk).first()
    if user is None:
        username = 'Alibaba_%s' % pk
        user = User.objects.create_user(id=pk, username=username)
    return user


def testserver_reverse(*args, **kwargs):
    """
    Prepend to reverse() prefix "http://testserver" which is default domain (+protocol) used by Django test Client.
    """
    return 'http://testserver%s' % reverse(*args, **kwargs)


merge = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, ["append"]),
        (dict, ["merge"])
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"]
).merge
