"""Auto schema sync — detect and fix column drift between SQLAlchemy models and Postgres.

SQLAlchemy's `Base.metadata.create_all` creates new tables but never alters existing
tables to add new columns. When upstream adds a column to a model, anyone with an
existing database gets silent failures (UndefinedColumn errors masked as
InFailedSQLTransactionError).

This module detects mismatches on startup and recreates affected tables.
"""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.graph import Base

logger = logging.getLogger(__name__)


def get_missing_columns(model_columns: set[str], db_columns: set[str]) -> set[str]:
    """Return columns in the model but not in the database."""
    return model_columns - db_columns


def get_extra_columns(model_columns: set[str], db_columns: set[str]) -> set[str]:
    """Return columns in the database but not in the model."""
    return db_columns - model_columns


async def sync_schemas(conn: AsyncConnection) -> list[str]:
    """Compare all SQLAlchemy model tables against the actual DB schema.

    For any table with column mismatches: drop and recreate it.
    Returns list of table names that were recreated.

    Safe to call on every startup — does nothing if schemas match.
    """
    recreated = []

    def _check_and_fix(sync_conn):
        """Synchronous inspection + fix (runs inside run_sync)."""
        inspector = inspect(sync_conn)
        existing_tables = set(inspector.get_table_names())

        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                # Table doesn't exist yet — create_all will handle it
                continue

            # Get model columns
            model_columns = {col.name for col in table.columns}

            # Get DB columns
            db_columns = {col["name"] for col in inspector.get_columns(table_name)}

            missing = get_missing_columns(model_columns, db_columns)
            extra = get_extra_columns(model_columns, db_columns)

            if missing or extra:
                detail = []
                if missing:
                    detail.append(f"missing from DB: {missing}")
                if extra:
                    detail.append(f"extra in DB: {extra}")
                logger.warning(
                    "Schema drift detected in '%s': %s — dropping and recreating table",
                    table_name,
                    ", ".join(detail),
                )
                # Drop and recreate this specific table
                table.drop(sync_conn, checkfirst=True)
                table.create(sync_conn, checkfirst=True)
                recreated.append(table_name)

    await conn.run_sync(_check_and_fix)

    if recreated:
        logger.warning("Recreated %d table(s) due to schema drift: %s", len(recreated), recreated)
    else:
        logger.info("Schema sync: all tables match models")

    return recreated
