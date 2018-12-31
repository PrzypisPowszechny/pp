import json
import requests
from django.conf import settings


class MailSendException(Exception):
    pass


def validate_single_receiver(receiver):
    if isinstance(receiver, str):
        mail, name = receiver, ''
    elif isinstance(receiver, tuple):
        mail, name = receiver
    else:
        raise ValueError('Receiver argument is unknown type {} (should be string or tuple)'.format(type(receiver)))
    return mail, name


def send_mail(receiver, subject, text, sender, recipient_variables=None,
              from_name='Przypis Powszechny'):
    """
    For multiple addresses recipient variables are always initialised
    so the recipient is not shown all other recipients.
    (see https://documentation.mailgun.com/en/latest/user_manual.html#batch-sending)
    :param receiver: an address string ot a tuple (address, address_name) or a list of tuples.
    :param subject:
    :param text:
    :param sender: name displayed before "@" character
    :param from_name: display name of the sender
    :return:
    """
    recipient_variables = recipient_variables or {}
    from_addr = '{}@{}'.format(sender, settings.PP_MAIL_DOMAIN)
    data = [
        ('from', '{} <{}>'.format(from_name, from_addr)),
        ('subject', subject),
        ('text', text),
    ]

    if isinstance(receiver, str) or isinstance(receiver, tuple):
        mail, name = validate_single_receiver(receiver)
        data.append(('to', '{} <{}>'.format(name, mail)))
    elif isinstance(receiver, list):
        for single in receiver:
            assert len(single) == 2, "Receiver is not in correct format: {}".format(single)
            mail, name = validate_single_receiver(single)
            recipient_variables.setdefault(mail, {}).update(recipient_variables.get(mail, {}))
            data.append(('to', '{} <{}>'.format(name, mail)))
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
