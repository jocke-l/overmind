from typing import Iterable

from . import command, parser
from .models import Message


def handshake(user: str, nick: str) -> Iterable[str]:
    return [
        command.nick(nick),
        command.user(user, mode="0", realname="ircbot-overmind"),
    ]
