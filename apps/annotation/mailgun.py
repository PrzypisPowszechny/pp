import json

import requests
from django.conf import settings


class MailSendException(Exception):
    pass


def receiver_to_param(receiver):
    if isinstance(receiver, str):
        addr, name = receiver, ''
    elif isinstance(receiver, tuple):
        addr, name = receiver
    else:
        raise ValueError('Receiver argument is unknown type {} (should be string or tuple)'.format(type(receiver)))
    return addr, name

def send_mail(to_addr, subject, text, sender, recipient_variables=None,
              from_name='Przypis Powszechny'):
    """
    For multiple addresses recipient variables are always initialised
    so the recipient is not shown all other recipients.
    (see https://documentation.mailgun.com/en/latest/user_manual.html#batch-sending)
    :param to_addr: an address string ot a tuple (address, address_name) or a list of tuples.
    :param subject:
    :param text:
    :param sender:
    :param from_name:
    :return:
    """
    recipient_variables = recipient_variables or {}
    from_addr = '{}@{}'.format(sender, settings.PP_MAIL_DOMAIN)
    data = [
        ('from', '{} <{}>'.format(from_name, from_addr)),
        ('subject', subject),
        ('text', text),
    ]

    if isinstance(to_addr, str) or isinstance(to_addr, tuple):
        addr, name = receiver_to_param(to_addr)
        data.append(('to', '{} <{}>'.format(name, addr)))
    elif isinstance(to_addr, list):
        for single in to_addr:
            assert len(single) == 2, "Receiver is not in correct format: {}".format(single)
            addr, name = receiver_to_param(single)
            recipient_variables.setdefault(addr, {}).update(recipient_variables.get(addr, {}))
            data.append(('to', '{} <{}>'.format(name, addr)))


        data.append(('recipient-variables', json.dumps(recipient_variables)))

    response = requests.post(
        settings.MAILGUN_API_URL,
        auth=('api', settings.MAILGUN_API_KEY),
        data=data,
    )

    if not (200 <= response.status_code < 300):
        msg = 'Request to {} unexpected status {}. Response: \n {}'.format(
            settings.MAILGUN_API_URL, response.status_code, response.content)
        if settings.DEBUG:
            msg += '\nYou are in DEBUG mode -- make sure you have set MAILGUN_API_KEY environment variable in your local environment.'
        raise MailSendException(msg)
