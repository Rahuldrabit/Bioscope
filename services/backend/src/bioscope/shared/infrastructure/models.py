"""Minimal SQLAlchemy metadata for the Phase 0 migration baseline."""

from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, func

metadata = MetaData()

platform_metadata = Table(
    "platform_metadata",
    metadata,
    Column("key", String(100), primary_key=True),
    Column("value", Text, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
