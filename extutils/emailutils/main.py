"""
Main utilities related to email.
"""
from threading import Thread
from typing import List, Optional, Tuple

import ttldict
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from env_var import is_testing
from JellyBot.systemconfig import Email

from .mock import EmailServer


class MailSender:
    """
    Mail sending class.

    Prevents duplicated/spamming emails by caching what have been sent.
    Same email could be sent once in ``Email.EmailCacheExpirySeconds`` seconds only.

    Sends email to mock server and will not send the email asynchronously
    if ``TEST`` in environment variables is set to ``1``.
    """
    _cache_ = ttldict.TTLOrderedDict(Email.EmailCacheExpirySeconds)

    @staticmethod
    def collate_info(
            content_html: str, recipients: Optional[List[str]] = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix) -> Tuple[str, List[str], str, str]:
        """
        Collate the info of an email to be sent and return the collated info.

        If ``recipients`` is ``None``, the email will be sent to ``settings.EMAIL_HOST_USER``.

        No subject prefix is ``prefix`` is set to ``None``.

        :param content_html: email content
        :param recipients: email recipient(s)
        :param subject: email subject
        :param prefix: email subject prefix
        :return: tuple containing the collated email info
        """
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
        Send an email to ``recipients``.

        ``content_html`` can be HTML.

        If ``recipients`` is ``None``, the email will be sent to ``settings.EMAIL_HOST_USER``.

        No subject prefix is ``prefix`` is set to ``None``.

        Will not send the email if the same content has been sent to the same recipient(s)
        within ``Email.EmailCacheExpirySeconds`` seconds.

        Sends email to mock server and will not send the email asynchronously
        if ``TEST`` in environment variables is set to ``1``.

        :param content_html: email content
        :param recipients: email recipient(s)
        :param subject: email subject
        :param prefix: email subject prefix
        """
        # TEST: Mail duplication preventing service

        if content_html not in MailSender._cache_:
            sender, recipients, subject, content_html = \
                MailSender.collate_info(content_html, recipients, subject, prefix)

            MailSender._cache_[content_html] = None

            if is_testing():
                print()
                print("--- SENDING EMAIL TO MOCK SERVER ---")
                print()
                MailSender.send_email_to_mock_server(sender, recipients, subject, content_html)
            else:
                send_mail(subject, strip_tags(content_html), sender, recipients, html_message=content_html)

    @staticmethod
    def send_email_async(
            content_html: str, recipients: List[str] = None, *,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        """
        Same as ``EmailSender.send_email()``. The only difference is that this sends the email asynchronously.
        """
        if is_testing():
            MailSender.send_email_to_mock_server(*MailSender.collate_info(content_html, recipients, subject, prefix))
        else:
            Thread(
                target=MailSender.send_email, args=(content_html,),
                kwargs={"recipients": recipients, "subject": subject, "prefix": prefix}).start()

    @staticmethod
    def send_email_to_mock_server(sender: str, recipients: List[str], subject: str, content: str):
        """
        Send an email to the mock server.

        :param sender: email sender
        :param recipients: email recipient(s)
        :param subject: email subject
        :param content: email content
        """
        print()
        print("--- SENDING EMAIL TO MOCK SERVER ---")
        print(f"Sender: {sender}")
        print(f"Recipient(s): {recipients}")
        print(f"Subject: {subject}")
        print(f"Content:\n{content}")
        print("---------------------")
        print()
        EmailServer.send_email(sender, recipients, subject, content)
