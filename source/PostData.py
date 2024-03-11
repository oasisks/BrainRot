from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

@dataclass
class PostData:
    user: str = ""
    title: str = ""
    text: str = ""
    images: List[bytes] = field(default_factory=lambda: [])
    replies: List[Reply] = field(default_factory=lambda: [])


@dataclass
class Reply:
    parent: Reply
    user: str = ""
    child: List[Reply] = field(default_factory=lambda: [])
    content: str = ""
    images: List[bytes] = field(default_factory=lambda: [])