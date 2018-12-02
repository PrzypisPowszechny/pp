import requests
from django.conf import settings

class MailSendException(Exception):
    pass

def send_mail(to_addr, subject, text, sender,
              from_name='Przypis Powszechny',
              to_name=None):
    from_addr = '{}@{}'.format(sender, settings.PP_MAIL_DOMAIN)
    response = requests.post(
        settings.MAILGUN_API_URL,
        auth=('api', settings.MAILGUN_API_KEY),
        data={'from': '{} <{}>'.format(from_name, from_addr),
              'to': '{} <{}>'.format(to_name, to_addr),
              'subject': subject,
              'text': text})

    if not (200 <= response.status_code < 300):
        msg = 'Request to {} unexpected status {}. Response: \n {}'.format(
            settings.MAILGUN_API_URL, response.status_code, response.content)
        if settings.DEBUG:
            msg += '\nYou are in DEBUG mode -- make sure you have set MAILGUN_API_KEY environment variable in your local environment.'
        raise MailSendException(msg)