import json
from logging import getLogger

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from . import ga_cookies
from .consumers import GAConsumer
from .cookies import is_iamstaff, iamstaff_set_cookie

logger = getLogger('pp.analytics')


@csrf_exempt
def init_ping(request):
    """
    View called by extension every time it starts, this is hook for things like setting cookies etc
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method accepted')

    response = HttpResponse(content_type='application/json', content=json.dumps({'iamstaff': is_iamstaff(request)}))

    # Set GA cookies, based on send data
    cookies = ga_cookies.set_cookies(request.POST)
    if not cookies:
        logger.info('No cookie data extracted from POST in init_ping')
    for cookie in cookies:
        response.set_cookie(**cookie)
    return response


def extension_uninstalled_hook(request):
    cid_value = ga_cookies.read_cid_from_cookie(request)
    if cid_value is None:
        logger.error('Cid cookie not set or malformed.')
    else:
        if not is_iamstaff(request):
            try:
                GAConsumer(cid_value).send_event_extension_uninstalled()
            except GAConsumer.ConsumingError as e:
                logger.error(str(e))

    return render_to_response('uninstalled.html')


def set_iamstaff(request):
    response = HttpResponse("You've already been." if is_iamstaff(request) else 'Now you are.')
    response.set_cookie(**iamstaff_set_cookie())
    return response
