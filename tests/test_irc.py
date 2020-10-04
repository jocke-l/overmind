import unittest

from overmind import irc


class ParseRawMessageTestCase(unittest.TestCase):
    def test_servername_prefix(self):
        message = irc.parser.parse_message(":servername.example.com NOTICE :foo")
        self.assertEqual(message.prefix.servername, "servername.example.com")
        self.assertIsNone(message.prefix.nick)
        self.assertIsNone(message.prefix.user)
        self.assertIsNone(message.prefix.host)
        self.assertTrue(message.is_server)

    def test_usermask_prefix(self):
        message = irc.parser.parse_message(
            ":eggs!spam@example.com PRIVMSG #channel :hello!"
        )
        self.assertEqual(message.prefix.nick, "eggs")
        self.assertEqual(message.prefix.user, "spam")
        self.assertEqual(message.prefix.host, "example.com")
        self.assertIsNone(message.prefix.servername)
        self.assertTrue(message.is_client)

    def test_command(self):
        message = irc.parser.parse_message(f"COMMAND some args :woo hoo")
        self.assertEqual(message.command, "COMMAND")
        self.assertListEqual(message.params, ["some", "args", "woo hoo"])

        message = irc.parser.parse_message("QUIT")
        self.assertEqual(message.command, "QUIT")
