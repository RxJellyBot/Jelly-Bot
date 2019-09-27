from multiprocessing import Pool, cpu_count

from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from JellyBot.systemconfig import Email


class MailSender:
    _POOL = None

    @classmethod
    def _check_init_(cls):
        if not cls._POOL:
            cls._POOL = Pool(cpu_count())

    @classmethod
    def send_email(cls, content_html: str, recipients: list = None,
                   subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        """
        :param content_html: The content of the email. Content can be html string.
        :param recipients: Recipients of the email. The email will be sent to `EMAIL_HOST_USER` if this is `None`.
        :param subject: The subject of the email.
        :param prefix: Prefix of the subject. Set to `None` means no prefix.
        """
        cls._check_init_()

        if recipients is None:
            recipients = [settings.EMAIL_HOST_USER]

        if prefix is not None:
            subject = prefix + subject

        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, strip_tags(content_html), email_from, recipients, html_message=content_html)

    @classmethod
    def send_email_async(cls, content_html: str, recipients: list = None,
                         subject: str = Email.DefaultSubject, prefix: str = Email.DefaultPrefix):
        cls._check_init_()

        MailSender._POOL.apply_async(
            send_mail, (content_html,), kwds={"recipients": recipients, "subject": subject, "prefix": prefix})
