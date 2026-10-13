"""Deterministic, confirmation-first medicine recognition."""

from __future__ import annotations

import re

from bioscope.modules.medicines.domain.models import MedicineCandidate
from bioscope.modules.medicines.infrastructure.repository import MedicineRepository


class MedicineIntakeService:
    def __init__(self, repository: MedicineRepository) -> None:
        self._repository = repository

    async def add_text_candidate(
        self, *, session_id: str, owner_id: str, raw_text: str
    ) -> MedicineCandidate:
        label = " ".join(raw_text.split())
        ingredients = _split_ingredients(label)
        return await self._repository.create_candidate(
            session_id=session_id,
            owner_id=owner_id,
            label=label,
            ingredients=ingredients,
            asset_id=None,
            provenance="USER_ENTERED_UNCONFIRMED",
        )

    async def recognize_demo_fixture(
        self, *, session_id: str, owner_id: str, asset_id: str, filename: str
    ) -> MedicineCandidate | None:
        """Recognize named test fixtures only; arbitrary photos are never guessed."""

        normalized = filename.lower()
        if "demo-aspirin" not in normalized:
            return None
        return await self._repository.create_candidate(
            session_id=session_id,
            owner_id=owner_id,
            label="Aspirin (DEMO OCR fixture)",
            ingredients=("acetylsalicylic acid",),
            asset_id=asset_id,
            provenance="DEMO_OCR_FIXTURE",
        )


def _split_ingredients(value: str) -> tuple[str, ...]:
    pattern = r"\s*(?:\+|,|/|\band\b)\s*"
    parts = [part.strip() for part in re.split(pattern, value, flags=re.IGNORECASE)]
    ingredients = tuple(part for part in parts if part)
    return ingredients or (value,)
