"""Auto schema sync — detect and fix column drift between SQLAlchemy models and Postgres.

SQLAlchemy's `Base.metadata.create_all` creates new tables but never alters existing
tables to add new columns. When upstream adds a column to a model, anyone with an
existing database gets silent failures (UndefinedColumn errors masked as
InFailedSQLTransactionError).

This module detects mismatches on startup and applies non-destructive ALTER TABLE
for missing columns. Only drops/recreates tables when columns are removed (rare).
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


def _compile_column_type(col) -> str:
    """Get the SQL type string for a SQLAlchemy column."""
    from sqlalchemy.dialects import postgresql
    return col.type.compile(dialect=postgresql.dialect())


def _get_column_default_sql(col) -> str | None:
    """Get the DEFAULT clause for a column, or None."""
    if col.server_default is not None:
        return col.server_default.arg.text if hasattr(col.server_default.arg, "text") else str(col.server_default.arg)
    if col.default is not None:
        # Python-side defaults (e.g. default=dict) can't become SQL DEFAULTs
        return None
    return None


async def sync_schemas(conn: AsyncConnection) -> list[str]:
    """Compare all SQLAlchemy model tables against the actual DB schema.

    - Missing columns → ALTER TABLE ADD COLUMN (data preserved)
    - Extra columns in DB → DROP and recreate table (with row count warning)

    Returns list of table names that were modified.
    """
    modified = []

    def _check_and_fix(sync_conn):
        """Synchronous inspection + fix (runs inside run_sync)."""
        inspector = inspect(sync_conn)
        existing_tables = set(inspector.get_table_names())

        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                continue

            model_columns = {col.name for col in table.columns}
            db_columns = {col["name"] for col in inspector.get_columns(table_name)}

            missing = get_missing_columns(model_columns, db_columns)
            extra = get_extra_columns(model_columns, db_columns)

            if not missing and not extra:
                continue

            # --- Handle missing columns: ALTER TABLE ADD COLUMN ---
            if missing and not extra:
                for col_name in missing:
                    col = table.c[col_name]
                    col_type = _compile_column_type(col)
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    default_sql = _get_column_default_sql(col)

                    ddl = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type}'
                    if default_sql:
                        ddl += f" DEFAULT {default_sql}"
                        # NOT NULL is safe with a default
                        if not col.nullable:
                            ddl += " NOT NULL"
                    else:
                        # No default — must be nullable to add to existing rows
                        ddl += " NULL"

                    logger.info(
                        "Schema sync: adding column '%s' to '%s' (%s)",
                        col_name, table_name, col_type,
                    )
                    sync_conn.execute(text(ddl))

                modified.append(table_name)
                continue

            # --- Handle extra columns (or mixed): drop and recreate ---
            # This is destructive — log row count as warning
            row_count = sync_conn.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar()

            detail = []
            if missing:
                detail.append(f"missing from DB: {missing}")
            if extra:
                detail.append(f"extra in DB: {extra}")

            logger.warning(
                "Schema sync: '%s' has removed columns (%s) — dropping and recreating table (%d rows will be lost)",
                table_name, ", ".join(detail), row_count,
            )
            table.drop(sync_conn, checkfirst=True)
            table.create(sync_conn, checkfirst=True)
            modified.append(table_name)

    await conn.run_sync(_check_and_fix)

    if modified:
        logger.info("Schema sync: modified %d table(s): %s", len(modified), modified)
    else:
        logger.info("Schema sync: all tables match models")

    return modified
