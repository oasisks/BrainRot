from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PostData:
    user: str = ""
    title: str = ""
    text: str = ""
    id: str = ""
    subreddit: str = ""
    images: List[bytes] = field(default_factory=lambda: [])
    replies: List[Reply] = field(default_factory=lambda: [])


@dataclass
class Reply:
    parent: Reply | None
    user: str = ""
    children: List[Reply] = field(default_factory=lambda: [])
    content: str = ""
    images: List[bytes] = field(default_factory=lambda: [])