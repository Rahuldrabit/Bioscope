"""Narrow opt-in ChEMBL molecule search client."""

from __future__ import annotations

from typing import Any

import httpx

from bioscope.shared.domain.errors import SourceUnavailable

CHEMBL_API_ROOT = "https://www.ebi.ac.uk/chembl/api/data"


class ChEMBLClient:
    def __init__(self, *, enabled: bool, client: httpx.AsyncClient | None = None) -> None:
        self._enabled = enabled
        self._client = client

    async def search(self, query: str, *, limit: int) -> list[dict[str, str]]:
        if not self._enabled:
            raise SourceUnavailable()
        client = self._client or httpx.AsyncClient(timeout=5.0)
        owns_client = self._client is None
        try:
            response = await client.get(
                f"{CHEMBL_API_ROOT}/molecule/search.json",
                params={"q": query, "limit": min(limit, 10)},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            molecules = payload.get("molecules", [])
            return [
                {
                    "chembl_id": str(item.get("molecule_chembl_id", "")),
                    "name": str(item.get("pref_name", "")),
                }
                for item in molecules
                if item.get("molecule_chembl_id")
            ]
        except (httpx.HTTPError, ValueError) as exc:
            raise SourceUnavailable() from exc
        finally:
            if owns_client:
                await client.aclose()
