"""Portfolio CRUD endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_pipeline.market import MARKET_TICKER_MAP
from app.db.connection import get_session
from app.models.observations import PortfolioPosition

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Reverse map: ticker -> node_id
TICKER_TO_NODE = {ticker: node_id for ticker, node_id in MARKET_TICKER_MAP.items()}


class PositionIn(BaseModel):
    ticker: str
    shares: float
    entry_price: float
    entry_date: str | None = None
    notes: str = ""


class PositionOut(BaseModel):
    id: int
    ticker: str
    node_id: str | None
    shares: float
    entry_price: float
    entry_date: str | None
    notes: str
    created_at: str

    model_config = {"from_attributes": True}


class PositionUpdate(BaseModel):
    shares: float | None = None
    entry_price: float | None = None
    notes: str | None = None


def _to_out(p: PortfolioPosition) -> PositionOut:
    return PositionOut(
        id=p.id,
        ticker=p.ticker,
        node_id=p.node_id,
        shares=p.shares,
        entry_price=p.entry_price,
        entry_date=p.entry_date.isoformat() if p.entry_date else None,
        notes=p.notes or "",
        created_at=p.created_at.isoformat() if p.created_at else "",
    )


@router.get("", response_model=list[PositionOut])
async def list_positions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PortfolioPosition).order_by(PortfolioPosition.created_at.desc()))
    return [_to_out(p) for p in result.scalars().all()]


@router.post("", response_model=PositionOut)
async def add_position(pos: PositionIn, session: AsyncSession = Depends(get_session)):
    ticker = pos.ticker.upper()
    node_id = TICKER_TO_NODE.get(ticker)

    entry_date = None
    if pos.entry_date:
        try:
            entry_date = datetime.fromisoformat(pos.entry_date)
        except ValueError:
            pass

    position = PortfolioPosition(
        ticker=ticker,
        node_id=node_id,
        shares=pos.shares,
        entry_price=pos.entry_price,
        entry_date=entry_date,
        notes=pos.notes,
    )
    session.add(position)
    await session.commit()
    await session.refresh(position)
    return _to_out(position)


@router.put("/{position_id}", response_model=PositionOut)
async def update_position(
    position_id: int,
    update: PositionUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(PortfolioPosition).where(PortfolioPosition.id == position_id))
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    if update.shares is not None:
        position.shares = update.shares
    if update.entry_price is not None:
        position.entry_price = update.entry_price
    if update.notes is not None:
        position.notes = update.notes

    await session.commit()
    await session.refresh(position)
    return _to_out(position)


@router.delete("/{position_id}")
async def delete_position(
    position_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(PortfolioPosition).where(PortfolioPosition.id == position_id))
    position = result.scalar_one_or_none()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    await session.delete(position)
    await session.commit()
    return {"status": "deleted", "id": position_id}


class PortfolioSummaryOut(BaseModel):
    positions: list[PositionOut]
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float
    mapped_node_ids: list[str]


@router.get("/summary", response_model=PortfolioSummaryOut)
async def get_portfolio_summary(session: AsyncSession = Depends(get_session)):
    """Portfolio with current values and P&L."""
    from app.data_pipeline.market import fetch_all_market_prices

    result = await session.execute(select(PortfolioPosition))
    positions = result.scalars().all()

    if not positions:
        return PortfolioSummaryOut(
            positions=[], total_value=0, total_cost=0, total_pnl=0, total_pnl_pct=0, mapped_node_ids=[]
        )

    # Fetch current prices
    tickers = [p.ticker for p in positions]
    try:
        prices = await fetch_all_market_prices(tickers)
    except Exception:
        prices = {}

    total_value = 0.0
    total_cost = 0.0
    mapped_nodes: set[str] = set()

    for p in positions:
        cost = p.shares * p.entry_price
        total_cost += cost
        price_data = prices.get(p.ticker, {})
        current_price = price_data.get("close", p.entry_price)
        total_value += p.shares * current_price
        if p.node_id:
            mapped_nodes.add(p.node_id)

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

    return PortfolioSummaryOut(
        positions=[_to_out(p) for p in positions],
        total_value=round(total_value, 2),
        total_cost=round(total_cost, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_pct=round(total_pnl_pct, 2),
        mapped_node_ids=list(mapped_nodes),
    )
