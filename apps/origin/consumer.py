import logging

import requests

logger = logging.getLogger('pp.origin_consumer')


class Consumer:

    class ConsumingError(BaseException):
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
            raise self.ConsumingError('{} request error: {}'.format(self.api_name, error.message))

        if not (200 <= response.status_code < 300):
            raise self.ConsumingError('{} request to {} unexpected status {}. Response: \n {}'.format(
                self.api_name, url, response.status_code, response.content)
            )

        try:
            json_data = response.json()
        except (TypeError, KeyError, ValueError):
            raise self.ConsumingError('{} response is malformed'.format(self.api_name))

        return json_data
