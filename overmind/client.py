import asyncio
import logging

from . import irc, network
from .irc import Message
from .network import Connection
from .settings import Settings

log = logging.getLogger(__name__)


async def process(connection: Connection, settings: Settings, message: Message) -> None:
    if message.command == "PING":
        await connection.writeline(irc.command.ping(*message.params))
    elif message.command == "001":
        await connection.writeline(irc.command.join(",".join(settings.channels)))


async def run(settings: Settings) -> None:
    connection = await network.connect(settings.server, settings.port, ssl=settings.ssl)
    await connection.writelines(irc.handshake(settings.nick, settings.user))
    async for raw_message in connection:
        message = irc.parser.parse_message(raw_message)
        await asyncio.Task(process(connection, settings, message))
