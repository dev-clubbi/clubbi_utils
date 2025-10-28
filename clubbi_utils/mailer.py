from dataclasses import dataclass, field
from typing import Optional, Protocol, List


@dataclass()
class EmailAttachment:
    content: str
    name: str


@dataclass
class Email:
    sender: str
    recipients: List[str]
    html_body: str
    raw_text_body: str
    subject: str
    attachments: List[EmailAttachment] = field(default_factory=list)
    headers: Optional[dict] = None


class Mailer(Protocol):
    async def send(self, email: Email) -> None:
        """protocol function"""
