import requests


class Consumer:
    api_name = None
    base_url = None

    def __init__(self, api_name=None, base_url=None):
        self.api_name = api_name or self.api_name
        self.base_url = base_url or self.base_url

    class ConsumingResponseError(BaseException):
        pass

    class ConsumingDataError(BaseException):
        pass

    def get(self, endpoint_path, params=None):
        url = '%s%s' % (self.base_url, endpoint_path)
        try:
            response = requests.get(
                url=url,
                params=params,
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        except requests.exceptions.RequestException as error:
            raise self.ConsumingResponseError(self.request_error(getattr(error, 'message', error)))

        if not (200 <= response.status_code < 300):
            raise self.ConsumingResponseError('{} request to {} unexpected status {}. Response: \n {}'.format(
                self.api_name, url, response.status_code, response.content)
            )

        try:
            json_data = response.json()
        except (TypeError, KeyError, ValueError):
            raise self.ConsumingResponseError('{} response is malformed and cannot be loaded as json'
                                              .format(self.api_name))

        return json_data

    def request_error(self, reason):
        return '{} request error: {}'.format(self.api_name, reason)
