from django.shortcuts import render
from apps.annotation.http_basicauth import logged_in_or_basicauth


@logged_in_or_basicauth()
def index(request):
    return render(request, 'index.html')
