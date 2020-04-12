import os
from threading import Thread
from typing import List, Optional, Tuple

import ttldict
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from JellyBot.systemconfig import Email

from .fake import EmailServer


class MailSender:
    _cache_ = ttldict.TTLOrderedDict(Email.EmailCacheExpirySeconds)

    @staticmethod
    def collate_info(
            content_html: str, recipients: Optional[List[str]] = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix) -> Tuple[str, List[str], str, str]:
        if recipients is None:
            recipients = [settings.EMAIL_HOST_USER]

        if prefix is not None:
            subject = prefix + subject

        sender = settings.EMAIL_HOST_USER

        return sender, recipients, subject, content_html

    @staticmethod
    def send_email(
            content_html: str, recipients: Optional[List[str]] = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        """
        :param content_html: The content of the email. Content can be html string.
        :param recipients: Recipients of the email. The email will be sent to `EMAIL_HOST_USER` if this is `None`.
        :param subject: The subject of the email.
        :param prefix: Prefix of the subject. Set to `None` means no prefix.
        """
        if content_html not in MailSender._cache_:
            sender, recipients, subject, content_html = \
                MailSender.collate_info(content_html, recipients, subject, prefix)

            MailSender._cache_[content_html] = None

            if bool(int(os.environ.get("TEST", 0))):
                print()
                print("--- SENDING EMAIL ---")
                print()
                EmailServer.send_email(sender, recipients, subject, content_html)
            else:
                send_mail(subject, strip_tags(content_html), sender, recipients, html_message=content_html)

    @staticmethod
    def send_email_async(
            content_html: str, recipients: List[str] = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        if bool(int(os.environ.get("TEST", 0))):
            MailSender.send_email_to_fake_server(*MailSender.collate_info(content_html, recipients, subject, prefix))
        else:
            Thread(
                target=MailSender.send_email, args=(content_html,),
                kwargs={"recipients": recipients, "subject": subject, "prefix": prefix}).start()

    @staticmethod
    def send_email_to_fake_server(sender: str, recipients: List[str], subject: str, content: str):
        print()
        print("--- SENDING EMAIL ---")
        print(f"Sender: {sender}")
        print(f"Recipient(s): {recipients}")
        print(f"Subject: {subject}")
        print(f"Content:\n{content}")
        print("---------------------")
        print()
        EmailServer.send_email(sender, recipients, subject, content)
