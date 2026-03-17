"""RSS news pipeline — fetches financial news from curated RSS feeds.

No API key required.  27 feeds covering macro, monetary policy, equities,
commodities, credit, currencies, and geopolitics.  Each feed is pre-mapped
to graph node IDs; individual articles are further refined via keyword_matcher.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from app.data_pipeline.keyword_matcher import match_text_to_nodes
from app.data_pipeline.retry import retry_async

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feed definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RSSFeed:
    url: str
    name: str
    default_node_ids: list[str] = field(default_factory=list)
    tier: int = 2  # 1=wire/official, 2=major outlet, 3=specialist


# Dedicated financial feeds (10)
DEDICATED_FEEDS: list[RSSFeed] = [
    RSSFeed(
        url="https://www.federalreserve.gov/feeds/press_all.xml",
        name="Federal Reserve",
        default_node_ids=["fed_funds_rate", "fed_balance_sheet", "rate_expectations"],
        tier=1,
    ),
    RSSFeed(
        url="https://feeds.bloomberg.com/markets/news.rss",
        name="Bloomberg Markets",
        default_node_ids=["sp500"],
        tier=1,
    ),
    RSSFeed(
        url="https://www.cnbc.com/id/100003114/device/rss/rss.html",
        name="CNBC Top News",
        default_node_ids=["sp500"],
        tier=2,
    ),
    RSSFeed(
        url="https://www.cnbc.com/id/20910258/device/rss/rss.html",
        name="CNBC Economy",
        default_node_ids=["us_gdp_growth", "unemployment_rate"],
        tier=2,
    ),
    RSSFeed(
        url="https://finance.yahoo.com/news/rssindex",
        name="Yahoo Finance",
        default_node_ids=["sp500"],
        tier=2,
    ),
    RSSFeed(
        url="https://oilprice.com/rss/main",
        name="OilPrice.com",
        default_node_ids=["wti_crude", "brent_crude"],
        tier=3,
    ),
    RSSFeed(
        url="https://www.mining.com/feed/",
        name="Mining.com",
        default_node_ids=["gold", "copper"],
        tier=3,
    ),
    RSSFeed(
        url="https://seekingalpha.com/market_currents.xml",
        name="Seeking Alpha",
        default_node_ids=["earnings_momentum"],
        tier=3,
    ),
    RSSFeed(
        url="https://feeds.feedburner.com/zerohedge/feed",
        name="ZeroHedge",
        default_node_ids=["geopolitical_risk_index"],
        tier=3,
    ),
    RSSFeed(
        url="https://www.investing.com/rss/news.rss",
        name="Investing.com",
        default_node_ids=["sp500"],
        tier=2,
    ),
]

# Google News topic feeds (17) — always live, aggregated from many sources
_GN_BASE = "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q="
GOOGLE_NEWS_FEEDS: list[RSSFeed] = [
    RSSFeed(f"{_GN_BASE}federal+reserve", "GN: Federal Reserve",
            ["fed_funds_rate", "rate_expectations"], tier=2),
    RSSFeed(f"{_GN_BASE}oil+prices", "GN: Oil Prices",
            ["wti_crude", "brent_crude"], tier=2),
    RSSFeed(f"{_GN_BASE}stock+market", "GN: Stock Market",
            ["sp500", "nasdaq"], tier=2),
    RSSFeed(f"{_GN_BASE}inflation+CPI", "GN: Inflation CPI",
            ["us_cpi_yoy", "pce_deflator"], tier=2),
    RSSFeed(f"{_GN_BASE}central+banks", "GN: Central Banks",
            ["fed_funds_rate", "ecb_rate"], tier=2),
    RSSFeed(f"{_GN_BASE}commodities+prices", "GN: Commodities",
            ["gold", "copper", "wti_crude"], tier=2),
    RSSFeed(f"{_GN_BASE}geopolitics+sanctions", "GN: Geopolitics",
            ["geopolitical_risk_index", "sanctions_pressure"], tier=2),
    RSSFeed(f"{_GN_BASE}interest+rates+bonds", "GN: Rates & Bonds",
            ["us_10y_yield", "us_2y_yield", "yield_curve_spread"], tier=2),
    RSSFeed(f"{_GN_BASE}US+jobs+employment", "GN: Jobs",
            ["unemployment_rate"], tier=2),
    RSSFeed(f"{_GN_BASE}forex+currencies+dollar", "GN: Forex",
            ["dxy_index", "eurusd", "usdjpy"], tier=2),
    RSSFeed(f"{_GN_BASE}earnings+guidance", "GN: Earnings",
            ["earnings_momentum", "revenue_growth"], tier=2),
    RSSFeed(f"{_GN_BASE}FOMC+rate+decision", "GN: FOMC",
            ["fed_funds_rate", "rate_expectations"], tier=2),
    RSSFeed(f"{_GN_BASE}credit+spreads+bonds", "GN: Credit",
            ["ig_credit_spread", "hy_credit_spread"], tier=2),
    RSSFeed(f"{_GN_BASE}VIX+volatility", "GN: Volatility",
            ["vix", "move_index"], tier=2),
    RSSFeed(f"{_GN_BASE}tariffs+trade+war", "GN: Trade",
            ["trade_policy_tariffs"], tier=2),
    RSSFeed(f"{_GN_BASE}housing+market+mortgage", "GN: Housing",
            ["us_housing"], tier=2),
    RSSFeed(f"{_GN_BASE}China+economy+PMI", "GN: China",
            ["china_pmi"], tier=2),
    RSSFeed(f"{_GN_BASE}BOJ+Bank+of+Japan+policy", "GN: BOJ",
            ["japan_boj_policy"], tier=2),
    RSSFeed(f"{_GN_BASE}eurozone+inflation+HICP+ECB", "GN: EU HICP",
            ["eu_hicp"], tier=2),
    RSSFeed(f"{_GN_BASE}consumer+confidence+sentiment+survey", "GN: Consumer Confidence",
            ["consumer_confidence"], tier=2),
]

ALL_FEEDS: list[RSSFeed] = DEDICATED_FEEDS + GOOGLE_NEWS_FEEDS


# ---------------------------------------------------------------------------
# Article model
# ---------------------------------------------------------------------------

@dataclass
class NewsArticle:
    title: str
    description: str
    source: str
    published_at: str
    url: str
    node_ids: list[str]
    node_scores: dict[str, float]  # node_id → confidence
    tier: int = 2


# ---------------------------------------------------------------------------
# RSS parsing
# ---------------------------------------------------------------------------

def _parse_rss_xml(xml_text: str, feed: RSSFeed) -> list[NewsArticle]:
    """Parse RSS/Atom XML into NewsArticle objects."""
    articles: list[NewsArticle] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        logger.warning("Failed to parse RSS XML from feed '%s'", feed.name)
        return articles

    # RSS 2.0: channel/item
    items = root.findall(".//item")
    if not items:
        # Atom: entry
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//atom:entry", ns)

    for item in items[:30]:  # Cap at 30 per feed to avoid noise
        title = _text(item, "title") or ""
        description = _text(item, "description") or _text(item, "summary") or ""
        link = _text(item, "link") or _attr(item, "link", "href") or ""
        pub_date = _text(item, "pubDate") or _text(item, "published") or _text(item, "updated") or ""

        if not title:
            continue

        # Strip HTML from description
        description = _strip_html(description)[:500]

        # Match to nodes: combine feed defaults + keyword matching
        matches = match_text_to_nodes(title, description)
        matched_node_ids = {nid for nid, _ in matches}
        node_scores = {nid: score for nid, score in matches}

        # Add feed defaults for nodes not already matched
        for default_nid in feed.default_node_ids:
            if default_nid not in matched_node_ids:
                matched_node_ids.add(default_nid)
                node_scores[default_nid] = 0.3  # Low confidence for default-only

        if not matched_node_ids:
            continue

        articles.append(NewsArticle(
            title=title.strip(),
            description=description.strip(),
            source=feed.name,
            published_at=pub_date.strip(),
            url=link.strip(),
            node_ids=list(matched_node_ids),
            node_scores=node_scores,
            tier=feed.tier,
        ))

    return articles


def _text(el: ET.Element, tag: str) -> str | None:
    """Get text of a child element, handling namespaces."""
    child = el.find(tag)
    if child is not None and child.text:
        return child.text
    # Try with Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    child = el.find(f"atom:{tag}", ns)
    if child is not None and child.text:
        return child.text
    return None


def _attr(el: ET.Element, tag: str, attr: str) -> str | None:
    """Get attribute of a child element (for Atom links)."""
    child = el.find(tag)
    if child is not None:
        return child.get(attr)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    child = el.find(f"atom:{tag}", ns)
    if child is not None:
        return child.get(attr)
    return None


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings (word-level)."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def deduplicate_articles(articles: list[NewsArticle], threshold: float = 0.6) -> list[NewsArticle]:
    """Remove near-duplicate articles using Jaccard similarity on titles."""
    unique: list[NewsArticle] = []
    for article in articles:
        is_dup = False
        for existing in unique:
            if _jaccard_similarity(article.title, existing.title) > threshold:
                is_dup = True
                # Keep the one from the higher-tier source
                if article.tier < existing.tier:
                    unique.remove(existing)
                    unique.append(article)
                break
        if not is_dup:
            unique.append(article)
    return unique


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

async def fetch_feed(feed: RSSFeed, client: httpx.AsyncClient) -> list[NewsArticle]:
    """Fetch and parse a single RSS feed."""
    try:
        async def _do_fetch():
            resp = await client.get(feed.url, follow_redirects=True)
            resp.raise_for_status()
            return resp.text

        xml_text = await retry_async(_do_fetch, label=f"RSS:{feed.name}")
        return _parse_rss_xml(xml_text, feed)
    except Exception as e:
        logger.warning("Failed to fetch RSS feed %s: %s", feed.name, e)
        return []


async def fetch_all_news_feeds(
    feeds: list[RSSFeed] | None = None,
) -> list[NewsArticle]:
    """Fetch all RSS feeds, deduplicate, and return sorted articles."""
    feeds = feeds or ALL_FEEDS
    all_articles: list[NewsArticle] = []

    async with httpx.AsyncClient(
        timeout=20.0,
        headers={"User-Agent": "CausalSentimentEngine/1.0"},
    ) as client:
        for feed in feeds:
            articles = await fetch_feed(feed, client)
            all_articles.extend(articles)

    # Deduplicate cross-source
    unique = deduplicate_articles(all_articles)

    # Sort: higher tier first, then by number of matched nodes (more relevant first)
    unique.sort(key=lambda a: (a.tier, -len(a.node_ids)))

    logger.info(
        "News fetch complete: %d articles from %d feeds (%d after dedup)",
        len(all_articles), len(feeds), len(unique),
    )
    return unique


async def fetch_news_for_node(node_id: str) -> list[NewsArticle]:
    """Fetch news relevant to a specific node (for agent tool)."""
    all_articles = await fetch_all_news_feeds()
    return [a for a in all_articles if node_id in a.node_ids][:15]


def detect_trending_topics(
    articles: list[NewsArticle],
    min_sources: int = 3,
) -> list[dict]:
    """Detect nodes with coverage from 3+ unique sources (trending signal)."""
    node_source_map: dict[str, set[str]] = {}
    for article in articles:
        for node_id in article.node_ids:
            node_source_map.setdefault(node_id, set()).add(article.source)

    trending = []
    for node_id, sources in node_source_map.items():
        if len(sources) >= min_sources:
            trending.append({
                "node_id": node_id,
                "source_count": len(sources),
                "sources": list(sources),
            })
    return sorted(trending, key=lambda t: -t["source_count"])


async def fetch_news_for_query(query: str, max_results: int = 15) -> list[NewsArticle]:
    """Fetch news matching a free-text query via Google News RSS."""
    encoded = query.replace(" ", "+")
    feed = RSSFeed(
        url=f"{_GN_BASE}{encoded}",
        name=f"GN: {query}",
        default_node_ids=[],
        tier=2,
    )
    async with httpx.AsyncClient(
        timeout=20.0,
        headers={"User-Agent": "CausalSentimentEngine/1.0"},
    ) as client:
        articles = await fetch_feed(feed, client)
    return articles[:max_results]
