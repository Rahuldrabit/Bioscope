"""Private local object storage for development and deterministic tests.

The adapter deliberately stores bytes outside PostgreSQL and exposes only opaque object keys.
"""

from __future__ import annotations

import asyncio
from pathlib import Path


class LocalPrivateObjectStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    async def put(self, key: str, content: bytes) -> None:
        path = self._path_for(key)
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, content)

    async def exists(self, key: str) -> bool:
        return await asyncio.to_thread(self._path_for(key).is_file)

    async def delete(self, key: str) -> None:
        path = self._path_for(key)
        if await asyncio.to_thread(path.exists):
            await asyncio.to_thread(path.unlink)

    def _path_for(self, key: str) -> Path:
        if not key or Path(key).name != key:
            raise ValueError("Object keys must be opaque file names")
        return self._root / key
