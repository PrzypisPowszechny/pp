"""
PP application is closed, do not add new models (or views) the only possible development activity is
further development of User class, which is the only member of this application and cannot be moved due to its
key role of project-wide user model.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_READER = 'reader'
    ROLE_EDITOR = 'editor'
    ROLE_CHOICES = (
        (ROLE_EDITOR, ROLE_EDITOR),
        (ROLE_READER, ROLE_READER),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_READER)
