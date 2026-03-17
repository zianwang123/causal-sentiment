"""Reddit data pipeline using asyncpraw for social sentiment."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from app.data_pipeline.keyword_matcher import match_text_to_node_ids

logger = logging.getLogger(__name__)

# Subreddits to monitor
MONITORED_SUBREDDITS = ["wallstreetbets", "economics", "stocks"]


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
                    node_ids = match_text_to_node_ids(post.title, post.selftext or "")
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
