"""Source registry and access-policy layer.

Each source must have an explicit access decision based on its actual
API/developer documentation and, when scraping is contemplated, its
Terms/robots policy. Unknown or prohibited access is treated as disabled.
"""

from dataclasses import dataclass
from typing import Literal

CollectionMethod = Literal["api", "scrape", "not_permitted"]


@dataclass(frozen=True)
class SourceConfig:
    name: str
    has_official_api: bool
    scraping_permitted: bool
    base_url: str
    api_docs_url: str | None = None
    terms_url: str | None = None
    robots_url: str | None = None
    access_verified_on: str | None = None
    requests_per_minute: int = 20
    notes: str = ""

    @property
    def method(self) -> CollectionMethod:
        if self.has_official_api:
            return "api"
        if self.scraping_permitted:
            return "scrape"
        return "not_permitted"


# IMPORTANT: these are still placeholders. Replace each entry only after
# verifying the real source's API/ToS/robots policy. Do not guess.
SOURCES: dict[str, SourceConfig] = {
    "airline_a": SourceConfig(
        name="airline_a",
        has_official_api=True,
        scraping_permitted=False,
        base_url="https://api.example-airline-a.com",
        api_docs_url="",
        terms_url="",
        access_verified_on="",
        requests_per_minute=20,
        notes="Example API adapter only. Replace with a verified official/partner API.",
    ),
    "airline_b": SourceConfig(
        name="airline_b",
        has_official_api=False,
        scraping_permitted=False, # Changed to False
        base_url="https://www.example-airline-b.com",
        terms_url="",
        robots_url="",
        access_verified_on="",
        requests_per_minute=12,
        notes="Example Playwright adapter only. Replace after explicit access verification.",
    ),
    "airline_c": SourceConfig(
        name="airline_c",
        has_official_api=False,
        scraping_permitted=False,
        base_url="https://www.example-airline-c.com",
        notes="Intentionally disabled until automated access is verified.",
    ),
}


def get_active_sources() -> dict[str, SourceConfig]:
    return {name: cfg for name, cfg in SOURCES.items() if cfg.method != "not_permitted"}
