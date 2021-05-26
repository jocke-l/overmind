import argparse
import asyncio
import functools
import logging
from typing import Any, Callable, Mapping, Tuple, TypeVar

from . import client
from .settings import Settings

T = TypeVar("T")

log = logging.getLogger(__name__)


def async_run(func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    def wrapper(*args: Tuple[Any, ...], **kwargs: Mapping[str, Any]) -> T:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@async_run
async def main() -> None:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--nick", type=str, required=True)
    argparser.add_argument("--user", type=str, required=True)
    argparser.add_argument("--server", type=str, required=True)
    argparser.add_argument("--port", type=int, default=6697)
    argparser.add_argument("--ssl", type=bool, default=True)
    argparser.add_argument("--channel", type=str, nargs="+", required=True)
    argparser.add_argument("--debug-level", type=str, default="INFO")
    args = argparser.parse_args()

    logging.basicConfig(level=args.debug_level)

    settings = Settings(
        nick=args.nick,
        user=args.user,
        server=args.server,
        port=args.port,
        ssl=args.ssl,
        channels=args.channel,
        autorestart=False,
    )

    while True:
        try:
            await client.run(settings)
        except BaseException as e:
            log.exception("Uncaught exception", exc_info=e)

        if not settings.autorestart:
            break
