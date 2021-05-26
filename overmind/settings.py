from dataclasses import dataclass
from typing import List


@dataclass
class Settings:
    nick: str
    user: str
    server: str
    port: int
    ssl: bool
    channels: List[str]
    autorestart: bool
