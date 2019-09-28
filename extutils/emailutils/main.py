from threading import Thread

import ttldict
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from JellyBot.systemconfig import Email


class MailSender:
    _cache_ = ttldict.TTLOrderedDict(Email.EmailCacheExpirySeconds)

    @staticmethod
    def send_email(
            content_html: str, recipients: list = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        """
        :param content_html: The content of the email. Content can be html string.
        :param recipients: Recipients of the email. The email will be sent to `EMAIL_HOST_USER` if this is `None`.
        :param subject: The subject of the email.
        :param prefix: Prefix of the subject. Set to `None` means no prefix.
        """
        if content_html in MailSender._cache_:
            if recipients is None:
                recipients = [settings.EMAIL_HOST_USER]

            if prefix is not None:
                subject = prefix + subject

            email_from = settings.EMAIL_HOST_USER
            MailSender._cache_[content_html] = None
            send_mail(subject, strip_tags(content_html), email_from, recipients, html_message=content_html)

    @staticmethod
    def send_email_async(
            content_html: str, recipients: list = None,
            subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):

        Thread(
            target=MailSender.send_email, args=(content_html,),
            kwargs={"recipients": recipients, "subject": subject, "prefix": prefix}).start()
