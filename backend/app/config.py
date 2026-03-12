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
    openai_model: str = "gpt-5.1"

    model_config = {"env_file": ["../.env", ".env"]}


settings = Settings()
