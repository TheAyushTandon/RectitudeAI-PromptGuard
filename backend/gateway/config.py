"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "RectitudeAI"
    app_version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # LLM
    llm_provider: Literal["openai", "anthropic", "ollama"] = "ollama"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Feature flags
    fhe_enabled: bool = False           # Real FHE — disabled until concrete-ml fixes
    fhe_simulated: bool = True          # Show simulated FHE in demo
    zkp_enabled: bool = False           # ZKP tool verification

    # Orchestrator
    prefilter_instant_block: float = 1.0    # Instant block threshold
    prefilter_escalate: float = 0.50        # Escalate threshold
    ml_block_threshold: float = 0.80
    ml_escalate_threshold: float = 0.50
    asi_alert_threshold: float = 0.45       # ASI risk score → force ML

    # Red team
    redteam_report_path: str = "logs/vulnerability_report.json"

    # FHE service URLs (only used when fhe_enabled=True)
    fhe_key_manager_url: str = "http://key-manager:8000"
    fhe_inference_url: str = "http://fhe-inference:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
