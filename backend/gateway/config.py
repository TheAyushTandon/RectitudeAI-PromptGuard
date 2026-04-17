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
    llm_provider: str = "groq"  # supports: openai, anthropic, ollama, mock, groq
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    default_model: str = "gemma:2b"

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
        extra = "ignore"


settings = Settings()
