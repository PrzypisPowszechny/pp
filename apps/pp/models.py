from django.contrib.auth.models import AbstractUser


# PP application is closed, do not add new models (or views) the only possible development activity is
# further development of User class, which is the only member of this application and cannot be moved due to its
# key role of project-wide user model.


class User(AbstractUser):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'users'
