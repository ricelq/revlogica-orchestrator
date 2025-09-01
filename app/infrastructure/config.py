# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/infrastructure/config.py

# This file will handle configuration, reading from environment variables for security and flexibility.
# It uses Pydantic's BaseSettings for structured configuration management.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_title: str = "VeriLogica Orchestrator API"
    api_version: str = "0.1.0"

    # URLs for external services
    nlp_service_url: str
    fuseki_url: str
    elasticsearch_url: str

    # eXist-DB Configuration
    existdb_url: str = "http://existdb:8080/exist/rest/db"
    exist_user: str = "admin"
    exist_password: str


settings = Settings()
