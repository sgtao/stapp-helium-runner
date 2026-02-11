# models.py
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class LinkItem:
    text: str
    original_url: str
    absolute_url: Optional[str] = None


@dataclass
class PageData:
    title: str
    base_url: str
    content: List[str]
    links: List[LinkItem] = field(default_factory=list)

    @property
    def unique_links_count(self) -> int:
        return len(
            {link.absolute_url for link in self.links if link.absolute_url}
        )
