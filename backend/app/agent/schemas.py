"""Tool definitions for the Claude agent."""

AGENT_TOOLS = [
    {
        "name": "fetch_fred_data",
        "description": "Fetch a macroeconomic data series from the FRED API. Returns the most recent observations with dates and values.",
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {
                    "type": "string",
                    "description": "FRED series ID (e.g., 'FEDFUNDS', 'CPIAUCSL', 'GDP', 'UNRATE', 'MANEMP')",
                },
                "observation_count": {
                    "type": "integer",
                    "description": "Number of most recent observations to return (default 10)",
                    "default": 10,
                },
            },
            "required": ["series_id"],
        },
    },
    {
        "name": "fetch_market_prices",
        "description": "Fetch recent market prices and daily percent changes for tracked ETFs and futures. Available tickers: SPY (S&P 500), QQQ (NASDAQ), IWM (Russell 2000), XLK (Tech), XLE (Energy), XLF (Financials), GLD (Gold), SLV (Silver), USO (Oil), UNG (Natural Gas), HG=F (Copper), ZW=F (Wheat), DX-Y.NYB (Dollar Index).",
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tickers to fetch (default: all tracked). E.g., ['SPY', 'GLD', 'USO']",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_news",
        "description": "Search for recent financial news articles by keyword query. Returns headlines, sources, and publication dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Federal Reserve interest rate decision', 'CPI inflation data')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of articles to return (default 10)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_sec_filings",
        "description": "Fetch SEC EDGAR financial data for a major company. Returns revenue, EPS, net income with recent quarterly trends and YoY growth. Available companies: AAPL, MSFT, AMZN, GOOGL, META, NVDA, JPM, GS, XOM, JNJ.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company": {
                    "type": "string",
                    "description": "Company ticker (e.g., 'AAPL', 'MSFT', 'NVDA')",
                },
                "form_type": {
                    "type": "string",
                    "description": "SEC form type: '10-K' (annual), '10-Q' (quarterly), '8-K' (current). Default: '10-Q'",
                    "default": "10-Q",
                },
            },
            "required": ["company"],
        },
    },
    {
        "name": "search_reddit",
        "description": "Search Reddit for social sentiment on financial topics. Returns top posts with scores and comment counts from subreddits like r/wallstreetbets, r/economics, r/stocks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subreddit": {
                    "type": "string",
                    "description": "Subreddit to search (default 'all'). Popular: 'wallstreetbets', 'economics', 'stocks'.",
                    "default": "all",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'inflation CPI', 'tech earnings', 'oil prices')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max posts to return (default 10)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "update_sentiment_signal",
        "description": "Write a sentiment signal to a node in the causal factor graph. The sentiment will be propagated to connected nodes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": "The graph node ID to update (e.g., 'fed_funds_rate', 'sp500', 'gold')",
                },
                "sentiment": {
                    "type": "number",
                    "description": "Sentiment score from -1.0 (very bearish) to 1.0 (very bullish)",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence in this assessment from 0.0 to 1.0",
                },
                "evidence": {
                    "type": "string",
                    "description": "Brief summary of the evidence supporting this sentiment assessment",
                },
            },
            "required": ["node_id", "sentiment", "confidence", "evidence"],
        },
    },
    {
        "name": "get_graph_neighborhood",
        "description": "Get a node's current state and its immediate neighbors with their sentiment values and edge weights.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": "The graph node ID to inspect",
                },
            },
            "required": ["node_id"],
        },
    },
]
