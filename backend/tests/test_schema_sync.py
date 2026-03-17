"""Tests for auto schema sync — detects column drift between models and DB."""

from sqlalchemy import Column, Float, Integer, String, MetaData, Table, inspect, text
from sqlalchemy.orm import DeclarativeBase

from app.db.schema_sync import get_missing_columns, get_extra_columns


class FakeBase(DeclarativeBase):
    pass


class FakeTable(FakeBase):
    __tablename__ = "fake_sync_test"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    score = Column(Float, nullable=True)


def test_get_missing_columns_detects_new_column():
    """If the model has a column the DB doesn't, it should be reported."""
    model_columns = {"id", "name", "score"}
    db_columns = {"id", "name"}  # score is missing
    missing = get_missing_columns(model_columns, db_columns)
    assert missing == {"score"}


def test_get_missing_columns_none_when_in_sync():
    """If model and DB match, no missing columns."""
    cols = {"id", "name", "score"}
    missing = get_missing_columns(cols, cols)
    assert missing == set()


def test_get_extra_columns_detects_removed_column():
    """If the DB has a column the model doesn't, it should be reported."""
    model_columns = {"id", "name"}
    db_columns = {"id", "name", "old_column"}
    extra = get_extra_columns(model_columns, db_columns)
    assert extra == {"old_column"}


def test_get_extra_columns_none_when_in_sync():
    cols = {"id", "name"}
    extra = get_extra_columns(cols, cols)
    assert extra == set()
