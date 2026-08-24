import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    origin: str = "http://localhost"
    public_origin: str = "http://localhost"
    database_url: str = "postgresql+psycopg://buscabase:buscabase-local@postgres:5432/buscabase"
    redis_url: str = "redis://redis:6379/0"
    cache_hmac_secret: str = "buscabase-local-hmac-key-not-for-production"
    cache_ttl_seconds: int = 604800
    log_ttl_seconds: int = 1209600
    uso_user: str = "uso"
    uso_password: str = ""

    bncc_dados_tag: str = "dados-2026.07.1"
    bncc_dados_owner: str = "bncc-dev"
    bncc_dados_repo: str = "bncc-dados"
    bncc_snapshot_dir: str = "/data/snapshots"
    bncc_catalog_dir: str = "/data/catalog"
    bncc_prose_dir: str = "/data/prose"
    github_api_url: str = "https://api.github.com"
    github_etag_path: str = "/data/snapshots/ETAG"

    openrouter_api_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""

    embedding_api_url: str = "https://openrouter.ai/api/v1"
    embedding_api_key: str = ""
    embedding_model: str = "google/gemini-embedding-001"
    embedding_dimension: int = 3072
    embedding_batch_size: int = 1
    embedding_timeout_seconds: int = 120

    rerank_api_url: str = "https://openrouter.ai/api/v1"
    rerank_api_key: str = ""
    rerank_model: str = "jina/jina-reranker-v3.5"
    rerank_timeout_seconds: int = 30
    rerank_top_k: int = 10
    rerank_candidates: int = 24
    retrieve_candidates: int = 80
    perguntar_source_limit: int = 6
    perguntar_item_source_limit: int = 4
    perguntar_prose_source_limit: int = 3
    perguntar_source_text_chars: int = 900

    generation_api_url: str = "https://openrouter.ai/api/v1"
    generation_api_key: str = ""
    generation_model: str = "deepseek/deepseek-v4-flash"
    generation_max_tokens: int = 700
    generation_temperature: float = 0.2
    generation_timeout_seconds: int = 120
    generation_extra_body: dict[str, Any] = Field(
        default_factory=lambda: {
            "thinking": {"type": "disabled"},
            "reasoning": {"enabled": False, "effort": "none"},
        }
    )

    perguntar_enabled: bool = True
    perguntar_queue_limit: int = 32
    perguntar_rate_limit_ip: int = 20
    perguntar_rate_window_seconds: int = 3600
    perguntar_session_limit: int = 12
    recado_rate_limit_ip: int = 5
    recado_rate_window_seconds: int = 3600

    log_level: str = "INFO"

    @field_validator("generation_extra_body", mode="before")
    @classmethod
    def parse_generation_extra_body(cls, value: Any) -> Any:
        default = {
            "thinking": {"type": "disabled"},
            "reasoning": {"enabled": False, "effort": "none"},
        }
        if value is None or value == "":
            return default
        if isinstance(value, str):
            return json.loads(value)
        return value

    def cloud_url(self, specific: str) -> str:
        return specific or self.openrouter_api_url

    def cloud_key(self, specific: str) -> str:
        return specific or self.openrouter_api_key


settings = Settings()
