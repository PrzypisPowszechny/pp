import responses
from django.conf import settings
from django.test import TestCase

from apps.annotation.mailgun import send_mail, MailSendException


class MailgunTest(TestCase):

    @responses.activate
    def test_request_sent(self):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))

        send_mail(
            to_addr='mock@mail.com',
            subject='',
            text='',
            sender='test',
        )

        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_batch_sent(self):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))

        send_mail(
            to_addr=[('mock1@mail.com', None), ('mock2@mail.com', None)],
            subject='',
            text='',
            sender='test',
        )

        self.assertEqual(len(responses.calls), 1)


    @responses.activate
    def test_400_exception_raised(self):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=400,
        ))

        with self.assertRaises(MailSendException):
            send_mail(
                to_addr='mock@mail.com',
                subject='',
                text='',
                sender='test',
            )

        self.assertEqual(len(responses.calls), 1)
