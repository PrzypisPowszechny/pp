
class DjangoRestUseDjangoAuthenticator(object):
    def authenticate(self, request=None):
        # Extract user from the encapsulated Django HTTP Request object to use Django authentication
        # instead of Django Rest Framework's
        user = getattr(request._request, 'user', None)
        return user, None
