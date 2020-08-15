from extutils.emailutils import EmailServer, MailSender
from tests.base import TestCase

__all__ = ["TestMockEmailServer", "TestMailSender"]

srv = EmailServer()


class TestMockEmailServer(TestCase):
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


class TestMailSender(TestCase):
    @classmethod
    def obj_to_clear(cls):
        return [MailSender]

    def test_no_duplicate(self):
        MailSender.send_email("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

        MailSender.send_email("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

    def test_no_duplicate_multiple_recipients(self):
        MailSender.send_email("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)
        self.assertEqual(len(srv.get_mailbox("recipient2").mails), 0)

        MailSender.send_email("Test content", ["recipient", "recipient2"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)
        self.assertEqual(len(srv.get_mailbox("recipient2").mails), 1)

    def test_no_duplicate_send_async(self):
        MailSender.send_email_async("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

        MailSender.send_email_async("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

    def test_no_duplicate_dfferent_recipient(self):
        MailSender.send_email("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)
        self.assertEqual(len(srv.get_mailbox("recipient2").mails), 0)

        MailSender.send_email("Test content", ["recipient2"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)
        self.assertEqual(len(srv.get_mailbox("recipient2").mails), 1)

    def test_no_duplicate_dfferent_content(self):
        MailSender.send_email("Test content", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

        MailSender.send_email("Test content 2", ["recipient"])

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 2)

    def test_no_duplicate_dfferent_subject(self):
        MailSender.send_email("Test content", ["recipient"], subject="Subject")

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 1)

        MailSender.send_email("Test content", ["recipient"], subject="Subject 2")

        self.assertEqual(len(srv.get_mailbox("recipient").mails), 2)
