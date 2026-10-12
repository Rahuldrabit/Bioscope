"""Phase 0 worker process placeholder with an explicit non-feature status."""

from __future__ import annotations

import asyncio
import logging

from bioscope.bootstrap.settings import get_settings


async def serve() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "BioScope worker started; no background jobs are registered in Phase 0",
        extra={"environment": settings.app_env, "demo_mode": settings.demo_mode},
    )
    await asyncio.Event().wait()


def main() -> None:
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("BioScope worker stopped")


if __name__ == "__main__":
    main()
