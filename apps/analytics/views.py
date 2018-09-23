from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response

from apps.analytics.cookies import set_ga_cookies, send_extension_uninstalled, read_cid_value


def init_ping(request):
    """
    View called by extension every time it starts, this is hook for things like setting cookies etc
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method accepted')

    response = HttpResponse()

    # Set GA cookies, based on send data
    cookies = set_ga_cookies(request.POST)
    for cookie in cookies:
        response.set_cookie(**cookie)
    return response


def extension_uninstalled(request):
    send_extension_uninstalled(cid_value=read_cid_value(request))
    return render_to_response('analytics.html')
