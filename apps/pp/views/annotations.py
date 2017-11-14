from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user

@allow_lazy_user
def get(request):
    # With allow lazy user, a new user is created at database for every request
    print(request.user.username)
    return HttpResponse()

