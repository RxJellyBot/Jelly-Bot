from django.test import TestCase

from extutils.emailutils import EmailServer


class TestFakeEmailServer(TestCase):
    def setUp(self) -> None:
        self.srv = EmailServer()

    def test_send_email_single_recipients(self):
        sender = "a"
        recipients = ["b"]
        subject = "Test subject"
        content = "Test content"

        self.srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = self.srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEquals(subject, mail.subject, "Mail subject not match.")
                self.assertEquals(content, mail.content, "Mail content not match.")
                self.assertEquals(sender, mail.sender, "Mail sender not match.")

    def test_send_email_multi_recipients(self):
        sender = "a"
        recipients = ["a", "b", "c", "d"]
        subject = "Test subject"
        content = "Test content"

        self.srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = self.srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEquals(subject, mail.subject, "Mail subject not match.")
                self.assertEquals(content, mail.content, "Mail content not match.")
                self.assertEquals(sender, mail.sender, "Mail sender not match.")

    def test_send_email_same_sender_recip(self):
        sender = "a"
        recipients = ["a"]
        subject = "Test subject"
        content = "Test content"

        self.srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = self.srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEquals(subject, mail.subject, "Mail subject not match.")
                self.assertEquals(content, mail.content, "Mail content not match.")
                self.assertEquals(sender, mail.sender, "Mail sender not match.")
