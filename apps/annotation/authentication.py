from rest_framework.authentication import SessionAuthentication


class IgnoreRefererSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        """
        Django REST has created this hacky solution of manually calling enforce_csrf, so to customize CSRF behaviour
        we have to wrap it instead of adding middleware etc.

        We remove referer, which in case of browser extension is worthless as we accept all requests coming from
        extension background and content-scripts.
        At the same time we use CSP and CSRF with the cookie accessible only on our website or by extension.
        """
        http_referer = request.META.get('HTTP_REFERER')
        if 'HTTP_HOST' in request.META:
            http_host = "https://%s/" % request.META['HTTP_HOST']
            request.META = request.META.copy()
            request.META['HTTP_REFERER'] = http_host
        try:
            super().enforce_csrf(request)
        finally:
            if http_referer:
                request.META['HTTP_REFERER'] = http_referer
            else:
                request.META.pop('HTTP_REFERER', None)
