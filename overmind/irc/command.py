from .models import Message


def _serialize_message(message: Message) -> str:
    raw_message_parts = [message.command]
    if len(message.params) > 1:
        raw_message_parts += message.params[:-1]
    raw_message_parts.append(f":{message.params[-1]}")

    return " ".join(raw_message_parts)


def _command(command: str, *args: str) -> str:
    return _serialize_message(Message(command=command, params=args))


def nick(name: str) -> str:
    return _command("NICK", name)


def user(name: str, *, mode: str, realname: str) -> str:
    return _command("USER", name, mode, "*", realname)


def join(*channels: str) -> str:
    return _command("JOIN", ",".join(channels))


def ping(*servers: str) -> str:
    return _command("PING", *servers)


def privmsg(target: str, message: str) -> str:
    return _command("PRIVMSG", target, message)
