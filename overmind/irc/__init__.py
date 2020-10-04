from typing import Iterable

from . import parser
from .models import Message


def serialize_message(message: Message) -> str:
    pass


def handshake(user: str, nick: str) -> Iterable[str]:
    messages = [
        Message(command="NICK", params=[nick]),
        Message(command="USER", params=[user, "0", "*"]),
    ]

    return map(serialize_message, messages)
