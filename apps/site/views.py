from django.shortcuts import render
from .http_basicauth import logged_in_or_basicauth


@logged_in_or_basicauth()
def site_test_index(request):
    return render(request, 'site/site_test_index.html')


def report_form(request):
    return render(request, 'site/report_form.html')
