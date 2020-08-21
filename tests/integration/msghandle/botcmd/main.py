from flags import ChannelType
from msghandle.botcmd.command import cmd_handler
from tests.base import TestCase, EventFactory

__all__ = ["TestBotCommandHandlerParse"]


class TestBotCommandHandlerParse(TestCase):
    def test_strip_left(self):
        cmds = [
            " JC ping",
            " JC\nping",
            "\nJC ping",
            "\nJC\nping"
        ]

        for cmd in cmds:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, "OK")

    def test_strip_both(self):
        cmds = [
            " JC ping ",
            " JC\nping ",
            " JC ping\n",
            " JC\nping\n",
            "\nJC ping ",
            "\nJC\nping ",
            "\nJC ping\n",
            "\nJC\nping\n"
        ]

        for cmd in cmds:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, "OK")

    def test_strip_right(self):
        cmds = [
            "JC ping ",
            "JC\nping ",
            "JC ping\n",
            "JC\nping\n"
        ]

        for cmd in cmds:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, "OK")

    def test_parse_space(self):
        cmd_resp_pair = [
            ("JC ping", "OK"),
            ("JC ping A", "OK\nText 1: A"),
            ("JC ping A B", "OK\nText 1: A\nText 2: B"),
            ("JC ping A B C", "OK\nText 1: A\nText 2: B C")
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_parse_nl(self):
        cmd_resp_pair = [
            ("JC\nping", "OK"),
            ("JC\nping\nA", "OK\nText 1: A"),
            ("JC\nping\nA\nB", "OK\nText 1: A\nText 2: B"),
            ("JC\nping\nA\nB\nC", "OK\nText 1: A\nText 2: B\nC")
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_parse_mixed(self):
        cmd_resp_pair = [
            "JC ping\nA",
            "JC\nping A"
        ]

        for cmd in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 0)

    def test_cmd_case_insensitive(self):
        cmd_resp_pair = [
            ("jc ping", "OK"),
            ("jc PING", "OK"),
            ("JC ping", "OK"),
            ("JC PING", "OK"),
            ("jc ping a", "OK\nText 1: a"),
            ("jc ping A", "OK\nText 1: A"),
            ("jc PING a", "OK\nText 1: a"),
            ("jc PING A", "OK\nText 1: A"),
            ("JC ping a", "OK\nText 1: a"),
            ("JC ping A", "OK\nText 1: A"),
            ("JC PING a", "OK\nText 1: a"),
            ("JC PING A", "OK\nText 1: A"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_space(self):
        cmd_resp_pair = [
            ('JC "ping" A', "OK\nText 1: A"),
            ('JC ping "A B"', "OK\nText 1: A B"),
            ('JC ping "A B C"', "OK\nText 1: A B C"),
            ('JC ping "A" B', "OK\nText 1: A\nText 2: B"),
            ('JC ping A "B"', "OK\nText 1: A\nText 2: B"),
            ('JC ping "A B" C', "OK\nText 1: A B\nText 2: C"),
            ('JC ping A "B C"', "OK\nText 1: A\nText 2: B C"),
            ('JC ping "A" B C', "OK\nText 1: A\nText 2: B C"),
            ('JC ping A "B" C', 'OK\nText 1: A\nText 2: "B" C'),
            ('JC ping A B "C"', 'OK\nText 1: A\nText 2: B "C"'),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_nl(self):
        cmd_resp_pair = [
            ('JC\n"ping"\nA', "OK\nText 1: A"),
            ('JC\nping\n"A\nB"', "OK\nText 1: A\nB"),
            ('JC\nping\n"A\nB\nC"', "OK\nText 1: A\nB\nC"),
            ('JC\nping\n"A"\nB', "OK\nText 1: A\nText 2: B"),
            ('JC\nping\nA\n"B"', "OK\nText 1: A\nText 2: B"),
            ('JC\nping\n"A\nB"\nC', "OK\nText 1: A\nB\nText 2: C"),
            ('JC\nping\nA\n"B\nC"', "OK\nText 1: A\nText 2: B\nC"),
            ('JC\nping\n"A"\nB\nC', "OK\nText 1: A\nText 2: B\nC"),
            ('JC\nping\nA\n"B"\nC', 'OK\nText 1: A\nText 2: "B"\nC'),
            ('JC\nping\nA\nB\n"C"', 'OK\nText 1: A\nText 2: B\n"C"'),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_mixed(self):
        cmd_resp_pair = [
            ('JC\nping\n"A B"', "OK\nText 1: A B"),
            ('JC\nping\n"A B C"', "OK\nText 1: A B C"),
            ('JC\nping\n"A B"\nC', "OK\nText 1: A B\nText 2: C"),
            ('JC\nping\nA\n"B C"', "OK\nText 1: A\nText 2: B C"),
            ('JC\nping\nA\nB "C" D', 'OK\nText 1: A\nText 2: B "C" D'),
            ('JC\nping\nA\nB\n"C"\nD', 'OK\nText 1: A\nText 2: B\n"C"\nD'),
            ('JC\nping\nA\nB\n"C" D', 'OK\nText 1: A\nText 2: B\n"C" D'),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_multi(self):
        cmd_resp_pair = [
            ("JC ping 'A B' 'C D'", "OK\nText 1: A B\nText 2: C D"),
            ("JC 'ping' 'A B' C D", "OK\nText 1: A B\nText 2: C D"),
            ("JC 'ping' A\nB 'C D'", "OK\nText 1: A\nB\nText 2: C D"),
            ("JC 'ping' 'A B' 'C D'", "OK\nText 1: A B\nText 2: C D"),
            ("JC\nping\n'A\nB'\n'C\nD'", "OK\nText 1: A\nB\nText 2: C\nD"),
            ("JC\n'ping'\n'A\nB'\nC\nD", "OK\nText 1: A\nB\nText 2: C\nD"),
            ("JC\n'ping'\nA B\n'C\nD'", "OK\nText 1: A B\nText 2: C\nD"),
            ("JC\n'ping'\n'A\nB'\n'C\nD'", "OK\nText 1: A\nB\nText 2: C\nD"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_diff_type(self):
        cmd_resp_pair = [
            ("JC ping 'A B'", "OK\nText 1: A B"),
            ('JC ping "A B"', "OK\nText 1: A B"),
            ("JC ping “A B”", "OK\nText 1: A B"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_uneven(self):
        cmd_resp_pair = [
            ("JC ping 'A 'B'", "OK\nText 1: A 'B"),
            ("JC ping 'A \"B'", "OK\nText 1: A \"B"),
            ("JC ping A' 'B C'D'", "OK\nText 1: A'\nText 2: B C'D"),
            ("JC ping '''", "OK\nText 1: '"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_quotation_mark_diff_ends(self):
        cmd_resp_pair = [
            ("JC ping 'A B\"", "OK\nText 1: 'A B\""),
            ("JC ping \"A B'", "OK\nText 1: \"A B'"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)

    def test_cmd_empty_param(self):
        cmd_resp_pair = [
            ("JC ping ''", "OK\nText 1: ''"),
            ("JC ping ", "OK"),
        ]

        for cmd, resp in cmd_resp_pair:
            with self.subTest(cmd):
                event = EventFactory.generate_text(
                    cmd, EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)
                result = cmd_handler.handle(event)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].content, resp)
