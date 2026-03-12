"""Reddit data pipeline using asyncpraw for social sentiment."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Subreddits to monitor
MONITORED_SUBREDDITS = ["wallstreetbets", "economics", "stocks"]

# Keyword → node_id mapping for matching posts to graph nodes
REDDIT_KEYWORD_MAP: dict[str, list[str]] = {
    "fed": ["fed_funds_rate", "rate_expectations"],
    "federal reserve": ["fed_funds_rate", "fed_balance_sheet"],
    "interest rate": ["fed_funds_rate", "us_2y_yield", "us_10y_yield"],
    "inflation": ["us_cpi_yoy", "pce_deflator"],
    "cpi": ["us_cpi_yoy"],
    "gdp": ["us_gdp_growth"],
    "unemployment": ["unemployment_rate"],
    "jobs": ["unemployment_rate"],
    "treasury": ["us_10y_yield", "us_30y_yield"],
    "yield": ["us_10y_yield", "yield_curve_spread"],
    "bonds": ["us_10y_yield", "us_30y_yield"],
    "credit": ["ig_credit_spread", "hy_credit_spread"],
    "oil": ["wti_crude"],
    "crude": ["wti_crude"],
    "gold": ["gold"],
    "copper": ["copper"],
    "vix": ["vix"],
    "volatility": ["vix", "move_index"],
    "spy": ["sp500"],
    "s&p": ["sp500"],
    "nasdaq": ["nasdaq"],
    "qqq": ["nasdaq"],
    "tech": ["tech_sector"],
    "banks": ["financials_sector"],
    "energy": ["energy_sector"],
    "dollar": ["dxy_index"],
    "usd": ["dxy_index"],
    "euro": ["eurusd"],
    "yen": ["usdjpy"],
    "china": ["china_pmi"],
    "tariff": ["trade_policy_tariffs"],
    "war": ["geopolitical_risk_index"],
    "geopolit": ["geopolitical_risk_index"],
    "sanction": ["sanctions_pressure"],
    "earnings": ["earnings_momentum"],
    "pe ratio": ["pe_valuations"],
    "revenue": ["revenue_growth"],
    "retail": ["retail_sentiment"],
    "sentiment": ["retail_sentiment"],
}


def _match_post_to_nodes(title: str, selftext: str = "") -> list[str]:
    """Match a post to graph nodes based on keyword matching."""
    text = (title + " " + selftext).lower()
    matched_nodes: set[str] = set()
    for keyword, node_ids in REDDIT_KEYWORD_MAP.items():
        if keyword in text:
            matched_nodes.update(node_ids)
    return list(matched_nodes)


async def fetch_reddit_posts(
    subreddits: list[str] | None = None,
    limit: int = 25,
) -> list[dict]:
    """Fetch top/hot posts from monitored subreddits.

    Returns list of dicts with: title, score, subreddit, url, selftext, node_ids, created_utc
    """
    try:
        import asyncpraw
    except ImportError:
        logger.warning("asyncpraw not installed — skipping Reddit fetch")
        return []

    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        logger.info("Reddit credentials not configured — skipping")
        return []

    subs = subreddits or MONITORED_SUBREDDITS
    posts: list[dict] = []

    try:
        reddit = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="causal-sentiment-engine/1.0",
        )

        for sub_name in subs:
            try:
                subreddit = await reddit.subreddit(sub_name)
                async for post in subreddit.hot(limit=limit):
                    node_ids = _match_post_to_nodes(post.title, post.selftext or "")
                    if not node_ids:
                        continue
                    posts.append({
                        "title": post.title,
                        "score": post.score,
                        "subreddit": sub_name,
                        "url": f"https://reddit.com{post.permalink}",
                        "selftext": (post.selftext or "")[:500],
                        "node_ids": node_ids,
                        "created_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                        "num_comments": post.num_comments,
                    })
            except Exception as e:
                logger.warning("Failed to fetch from r/%s: %s", sub_name, e)

        await reddit.close()
    except Exception as e:
        logger.exception("Reddit API error: %s", e)

    # Sort by score (highest first)
    posts.sort(key=lambda p: p["score"], reverse=True)
    logger.info("Reddit fetch: %d relevant posts from %d subreddits", len(posts), len(subs))
    return posts


async def search_reddit_for_agent(
    subreddit: str = "all",
    query: str = "",
    limit: int = 10,
) -> list[dict]:
    """Search Reddit for the agent tool — returns top posts matching query."""
    try:
        import asyncpraw
    except ImportError:
        return []

    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        return [{"error": "Reddit credentials not configured"}]

    results: list[dict] = []
    try:
        reddit = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="causal-sentiment-engine/1.0",
        )

        sub = await reddit.subreddit(subreddit)
        async for post in sub.search(query, limit=limit, sort="relevance", time_filter="week"):
            results.append({
                "title": post.title,
                "score": post.score,
                "subreddit": str(post.subreddit),
                "url": f"https://reddit.com{post.permalink}",
                "selftext": (post.selftext or "")[:300],
                "num_comments": post.num_comments,
                "created_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
            })

        await reddit.close()
    except Exception as e:
        logger.exception("Reddit search error: %s", e)

    return results
