"""
Module containing all required components of a mocking email server.
"""
from dataclasses import dataclass, field
from typing import List

from mixin import ClearableMixin


@dataclass
class EmailEntry:
    """
    Class representing a single email.
    """
    sender: str
    subject: str
    content: str


@dataclass
class EmailBox:
    """
    Class representing a mocking email box.
    """
    owner: str
    mails: List[EmailEntry] = field(default_factory=list)

    def get_mail_with_content(self, partial_content: str, *, first=False) -> List[EmailEntry]:
        """
        Get the email(s) which content contains ``partial_content``.

        :param partial_content: partial content of the email(s) to get
        :param first: if returning the first matching email only
        :return: list of emails which content contains `partial_content`
        """
        ret = []

        for mail in self.mails:
            if partial_content in mail.content:
                ret.append(mail)
                if first:
                    break

        return ret

    def get_mail_with_subject(self, subject_keyword: str, *, exact=False, first=False) -> List[EmailEntry]:
        """
        Get the email(s) which subject contains ``subject_keyword`` if ``exact`` is set to ``False``.

        Otherwise, get the email(s) with the subject ``subject_keyword``.

        :param subject_keyword: subject keyword of the email(s) to get
        :param exact" if the subject must match exactly
        :param first: if returning the first matching email only
        :return: list of emails which content contains `subject_keyword`
        """
        ret = []

        for mail in self.mails:
            if (exact and mail.subject == subject_keyword) or subject_keyword in mail.subject:
                ret.append(mail)
                if first:
                    break

        return ret


class EmailServer(ClearableMixin):
    """
    Class representing a mocking email server.
    """
    storage = {}

    @classmethod
    def clear(cls):
        """
        Clear the storage of the mocking email server.
        """
        cls.storage = {}

    @classmethod
    def get_mailbox(cls, owner: str) -> EmailBox:
        """
        Get the ``owner``'s mailbox.

        If the mailbox does not exist, create one and return it.

        :param owner: owner of the mailbox to get
        :return: email box of the owner
        """
        if owner not in cls.storage:
            cls.storage[owner] = EmailBox(owner)

        return cls.storage[owner]

    @classmethod
    def send_email(cls, sender: str, recipients: List[str], subject: str, content: str):
        """
        Send an email from ``sender`` to ``recipients``.

        :param sender: sender of the email
        :param recipients: recipient(s) of the email
        :param subject: subject of the email
        :param content: content of the email
        """
        entry = EmailEntry(sender=sender, subject=subject, content=content)
        for recipient in recipients:
            cls.get_mailbox(recipient).mails.append(entry)
