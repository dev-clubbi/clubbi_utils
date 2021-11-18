from unittest import IsolatedAsyncioTestCase

import aiobotocore

from clubbi.aws.ses_mailer import SesMailer
from clubbi.mailer import Email, EmailAttachment
from tests.aws.localstack_targets import create_test_client


class TestSesMailer(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        super().setUp()
        self._session = aiobotocore.get_session()
        async with create_test_client(self._session, 'ses') as ses:
            await ses.verify_domain_identity(Domain='test.io')

    async def test_it_send_email(self):
        async with create_test_client(self._session, 'ses') as ses_client:
            mailer = SesMailer(ses_client)

            await mailer.send(Email(
                sender='sender@test.io',
                recipients=['receiver@test.io'],
                html_body='''<html>
    <head></head>'
    <body>
    <p><b>Clubbi</b></p>
    <p>Teste</p>
    </body></html>''',
                raw_text_body='teste',
                subject='teste'
            ))

    async def test_it_send_email_with_attachments(self):
        async with create_test_client(self._session, 'ses') as ses_client:
            mailer = SesMailer(ses_client)
            await mailer.send(Email(
                sender='sender@test.io',
                recipients=['receiver@test.io'],
                html_body='''<html>
            <head></head>'
            <body>
            <p><b>Clubbi</b></p>
            <p>Teste</p>
            </body></html>''',
                raw_text_body='teste',
                subject='teste',
                attachments=[
                    EmailAttachment(
                        name='file.csv',
                        content='\n'.join(['nome,idade', 'Danilo,26', 'Sardinha,2' + 'Berinjela,2'])),
                    EmailAttachment(
                        name='file.csv',
                        content='\n'.join(['produto,preço', 'sabão,2.6', 'detergente,1.59' + 'abacate,2.58']))

                ]
            ))
