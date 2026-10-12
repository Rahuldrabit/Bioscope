import pytest
from sqlalchemy import text

from bioscope.shared.infrastructure.db import Database, SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_on_exception() -> None:
    database = Database("sqlite+aiosqlite:///:memory:")
    try:
        async with database.session() as session:
            await session.execute(text("CREATE TABLE sample (value INTEGER NOT NULL)"))
            await session.commit()

        with pytest.raises(RuntimeError, match="force rollback"):
            async with SqlAlchemyUnitOfWork(database) as unit_of_work:
                assert unit_of_work.session is not None
                await unit_of_work.session.execute(text("INSERT INTO sample VALUES (1)"))
                raise RuntimeError("force rollback")

        async with database.session() as session:
            count = await session.scalar(text("SELECT COUNT(*) FROM sample"))
        assert count == 0
    finally:
        await database.close()
