from dataclasses import dataclass, field
from typing import List


@dataclass
class EmailEntry:
    sender: str
    subject: str
    content: str


@dataclass
class EmailBox:
    owner: str
    mails: List[EmailEntry] = field(default_factory=list)

    def get_mail_with_content(self, partial_content: str, *, first=False) -> List[EmailEntry]:
        ret = []

        for mail in self.mails:
            if partial_content in mail.content:
                ret.append(mail)
                if first:
                    break

        return ret

    def get_mail_with_subject(self, partial_subject: str, *, exact=False, first=False) -> List[EmailEntry]:
        ret = []

        for mail in self.mails:
            if (exact and mail.subject == partial_subject) or partial_subject in mail.subject:
                ret.append(mail)
                if first:
                    break

        return ret


class EmailServer:
    storage = {}

    @classmethod
    def get_mailbox(cls, owner: str) -> EmailBox:
        if owner not in cls.storage:
            cls.storage[owner] = EmailBox(owner)

        return cls.storage[owner]

    @classmethod
    def send_email(cls, sender: str, recipients: List[str], subject: str, content: str):
        entry = EmailEntry(sender=sender, subject=subject, content=content)
        for recipient in recipients:
            cls.get_mailbox(recipient).mails.append(entry)
