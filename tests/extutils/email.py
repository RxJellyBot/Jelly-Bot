from extutils.emailutils import EmailServer
from tests.base import TestCase

__all__ = ["TestFakeEmailServer"]

srv = EmailServer()


class TestFakeEmailServer(TestCase):
    @staticmethod
    def obj_to_clear():
        return [srv]

    def test_send_email_single_recipients(self):
        sender = "a"
        recipients = ["b"]
        subject = "Test subject"
        content = "Test content"

        srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEqual(subject, mail.subject, "Mail subject not match.")
                self.assertEqual(content, mail.content, "Mail content not match.")
                self.assertEqual(sender, mail.sender, "Mail sender not match.")

    def test_send_email_multi_recipients(self):
        sender = "a"
        recipients = ["a", "b", "c", "d"]
        subject = "Test subject"
        content = "Test content"

        srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEqual(subject, mail.subject, "Mail subject not match.")
                self.assertEqual(content, mail.content, "Mail content not match.")
                self.assertEqual(sender, mail.sender, "Mail sender not match.")

    def test_send_email_same_sender_recip(self):
        sender = "a"
        recipients = ["a"]
        subject = "Test subject"
        content = "Test content"

        srv.send_email(sender, recipients, subject, content)

        for recipient in recipients:
            with self.subTest(recipient=recipient):
                mailbox = srv.get_mailbox(recipient)

                mails = mailbox.get_mail_with_content(content, first=True)
                self.assertGreater(
                    len(mails), 0,
                    f"Mailbox of {recipient} is empty.")

                mail = mails[0]
                self.assertEqual(subject, mail.subject, "Mail subject not match.")
                self.assertEqual(content, mail.content, "Mail content not match.")
                self.assertEqual(sender, mail.sender, "Mail sender not match.")
