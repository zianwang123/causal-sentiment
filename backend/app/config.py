from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cs_user:cs_password@localhost:5432/causal_sentiment"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    fred_api_key: str = ""
    newsapi_key: str = ""
    sec_edgar_user_agent: str = ""

    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"

    # Propagation
    propagation_max_depth: int = 4
    propagation_decay_per_hop: float = 0.3
    propagation_min_threshold: float = 0.01
    propagation_blend_ratio: float = 0.3

    # Agent
    agent_max_tool_rounds: int = 25

    # Anomaly detection
    anomaly_z_threshold: float = 2.0
    anomaly_min_observations: int = 5

    # Correlations
    correlation_bucket_hours: int = 3
    correlation_min_data_points: int = 3
    correlation_lookback_days: int = 90
    correlation_direction_flip_threshold: float = 0.3

    # Weights & decay
    sentiment_half_life_hours: float = 24.0
    sentiment_decay_skip_hours: float = 6.0
    edge_weight_base_ratio: float = 0.6
    centrality_cache_ttl: int = 300

    model_config = {"env_file": ["../.env", ".env"]}


settings = Settings()
