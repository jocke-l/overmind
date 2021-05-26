from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True)
class Prefix:
    nick: Optional[str] = None
    user: Optional[str] = None
    host: Optional[str] = None
    servername: Optional[str] = None


@dataclass(frozen=True)
class Message:
    command: str
    params: Sequence[str] = field(default_factory=list)
    prefix: Optional[Prefix] = None

    @property
    def is_server(self):
        return self.prefix.servername is not None

    @property
    def is_client(self):
        return not self.is_server
