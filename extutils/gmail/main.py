from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from JellyBotAPI.SystemConfig import Email


class MailSender:
    @staticmethod
    def send_email(content_html: str, recipients: list = None, subject: str = Email.DefaultSubject):
        if recipients is None:
            recipients = [settings.EMAIL_HOST_USER]

        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, strip_tags(content_html), email_from, recipients, html_message=content_html)
