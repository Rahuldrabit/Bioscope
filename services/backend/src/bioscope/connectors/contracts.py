"""Small source adapter contracts; provider payloads never enter domain code directly."""

from __future__ import annotations

from typing import Protocol


class MoleculeSearchAdapter(Protocol):
    async def search(self, query: str, *, limit: int) -> list[dict[str, str]]: ...
