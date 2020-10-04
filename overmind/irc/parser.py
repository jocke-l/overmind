import functools
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    TypeVar,
    Union,
)

from .models import Message, Prefix

T = TypeVar("T")
S = TypeVar("S")


class ParseError(Exception):
    pass


class InputExhausted(Exception):
    pass


def coroutine(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator used to automatically prime a coroutine.
    """

    @functools.wraps(func)
    def start(*args: Iterable[Any], **kwargs: Mapping[str, Any]):
        coro = func(*args, **kwargs)
        coro.send(None)
        return coro

    return start


def send_to(coro: Generator[None, T, S], values: Iterable[T]) -> S:
    """
    Convenience function used send values to a coroutine and get its
    return value when it completes. Sort of like `yield from` but not
    quite.
    """

    try:
        for value in values:
            coro.send(value)
        coro.throw(InputExhausted)  # TODO: Figure out a better way.
    except StopIteration as e:
        return e.value
    else:
        return send_to(coro, [])  # TODO: Figure out a better way.


@coroutine
def match_until(
    stop_char: Union[str, type(Ellipsis)], *, optional: bool = False
) -> Generator[None, str, Optional[str]]:
    """
    A coroutine that accumulates characters until `stop_char` is
    encountered, then returns the accumulator as a string.

    If `Ellipsis` is used as `stop_char` then all characters are
    accumulated and returned.

    If `optional` is `True` then `ParseError` is _not_ raised if the
    input stream doesn't contain `stop_char`.
    """
    result = []
    try:
        while (char := (yield)) != stop_char:
            # TODO: Figure out why this coroutine doesn't need to be primed.
            # TODO: Figure out why `char` seemingly random becomes `None`.
            if char is not None:
                result.append(char)
    except InputExhausted:  # TODO: Figure out a better way.
        if not optional and stop_char is not Ellipsis:
            raise ParseError(f"Never found expecetd char `{stop_char}`")

    return "".join(result)


@coroutine
def parse_usermask() -> Generator[None, str, Prefix]:
    nick = yield from match_until("!")
    user = yield from match_until("@")
    host = yield from match_until(...)

    return Prefix(nick=nick, user=user, host=host)


@coroutine
def parse_prefix() -> Generator[None, str, Prefix]:
    prefix = yield from match_until(" ")
    if all(char in prefix for char in "!@"):
        return send_to(parse_usermask(), prefix)
    else:
        return Prefix(servername=prefix)


@coroutine
def parse_command() -> Generator[None, str, str]:
    return (yield from match_until(" ", optional=True))


@coroutine
def parse_params() -> Generator[None, str, List[str]]:
    yield  # TODO: Figure out why this coroutine doesn't need to be primed.
    params = []
    try:
        while True:
            if (char := (yield)) != ":":
                params.append(char + (yield from match_until(" ", optional=True)))
            else:
                params.append((yield from match_until(...)))
                break
    except InputExhausted:  # TODO: Figure out a better way.
        pass

    return params


@coroutine
def parse() -> Generator[None, str, Message]:
    command_parser = parse_command()
    if (first_char := (yield)) == ":":
        prefix = yield from parse_prefix()
    else:
        # Send first character to the command parser since we've already consumed it.
        command_parser.send(first_char)
        prefix = None

    command = yield from command_parser
    params = yield from parse_params()

    return Message(command=command, params=params, prefix=prefix)


def parse_message(raw_message: str) -> Message:
    return send_to(parse(), raw_message)
