import requests


class Consumer:

    class ConsumingResponseError(BaseException):
        pass

    class ConsumingDataError(BaseException):
        pass

    api_name = None
    base_url = None

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
