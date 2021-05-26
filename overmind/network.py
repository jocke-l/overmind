import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from typing import Iterable

log = logging.getLogger(__name__)


class Connection:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer

    async def write(self, message: bytes) -> None:
        self.writer.write(message)
        await self.writer.drain()

    async def readline(self, sep="\r\n") -> str:
        line = (await self.reader.readuntil(sep.encode())).decode()
        log.debug("receiving: %s", line)
        return line

    async def writeline(self, line: str, *, sep="\r\n") -> None:
        log.debug("sedning: %s", line)
        await self.write((line + sep).encode())

    async def writelines(self, lines: Iterable[str], *, sep="\r\n") -> None:
        for line in lines:
            await self.writeline(line, sep=sep)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            while True:
                return await self.readline()
        except asyncio.exceptions.IncompleteReadError:
            raise StopAsyncIteration


async def connect(server: str, port: int = 6697, *, ssl: bool = True) -> Connection:
    return Connection(*await asyncio.open_connection(server, port, ssl=ssl, limit=4096))
