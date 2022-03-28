from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv

from aiobotocore.client import AioBaseClient

from clubbi_utils.logging import logger
from clubbi_utils.mailer import Email

CLUBBI_CONTROL_EMAIL = getenv("CLUBBI_CONTROL_EMAIL", "success@simulator.amazonses.com")


class SesMailer:
    def __init__(self, client: AioBaseClient):
        self.client = client
        self._charset = "UTF-8"

    async def send(self, email: Email) -> None:
        if email.attachments:
            response = await self.client.send_raw_email(**self._build_raw_email(email))
        else:
            response = await self.client.send_email(**self._build_email_data(email))
        logger.info(response["MessageId"])

    def _build_email_data(self, email: Email) -> dict:
        return dict(
            Destination={"ToAddresses": email.recipients, "BccAddresses": [CLUBBI_CONTROL_EMAIL]},
            Message={
                "Body": {
                    "Html": {
                        "Charset": self._charset,
                        "Data": email.html_body,
                    },
                    "Text": {
                        "Charset": self._charset,
                        "Data": email.raw_text_body,
                    },
                },
                "Subject": {
                    "Charset": self._charset,
                    "Data": email.subject,
                },
            },
            Source=email.sender,
        )

    def _build_raw_email(self, email: Email) -> dict:
        msg = MIMEMultipart()
        msg["Subject"] = email.subject
        msg["From"] = email.sender
        msg["To"] = email.recipients[0]

        msg_body = MIMEMultipart("alternative")
        # the message body
        text_part = MIMEText(email.raw_text_body, "plain", self._charset)
        html_part = MIMEText(email.html_body, "html", self._charset)

        # Add the text and HTML parts to the child container.
        msg_body.attach(text_part)
        msg_body.attach(html_part)

        msg.attach(msg_body)

        for attachment in email.attachments:
            part = MIMEApplication(attachment.content)
            part.add_header("Content-Disposition", "attachment", filename=attachment.name)
            msg.attach(part)

        return dict(Source=email.sender, Destinations=email.recipients, RawMessage={"Data": msg.as_string()})
