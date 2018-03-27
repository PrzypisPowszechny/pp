from django.shortcuts import render
from apps.pp.http_auth import logged_in_or_basicauth


@logged_in_or_basicauth()
def index(request):
    return render(request, 'index.html')
