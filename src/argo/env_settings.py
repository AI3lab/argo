from typing import Optional, Union, List
from pydantic import AnyHttpUrl, field_validator, BaseModel
from dotenv import load_dotenv
from decouple import config, Csv

load_dotenv()


class EnvSettings(BaseModel):
    API_HOST: str = config("API_HOST", default="127.0.0.1", cast=str)
    API_PORT: int = config("API_PORT", default=8000, cast=int)
    API_DEBUG: bool = config("API_DEBUG", default=False, cast=bool)
    WS_HOST: str = config("WS_HOST", default="127.0.0.1", cast=str)
    WS_PORT: int = config("WS_PORT", default=8001, cast=int)
    UPLOAD_DIR: str = config("UPLOAD_DIR", default="uploads", cast=str)


    REGISTER_AGENT_TO_RELAY:bool = config("REGISTER_AGENT_TO_RELAY", default=True, cast=bool)

    DATABASE_TYPE:  str = config("DATABASE_TYPE", default="mongodb", cast=str)
    DATABASE_URL:  str = config("DATABASE_URL", default="mongodb://localhost:27017/", cast=str)
    DATABASE_NAME: str = config("DATABASE_NAME", default="", cast=str)

    LLM_MODEL: str = config("LLM_MODEL", default="", cast=str)
    LLM_BASE_URL: str = config("LLM_BASE_URL", default="", cast=str)
    LLM_KEY: str = config("LLM_KEY", default="", cast=str)

    REDIS_HOST: str = config("REDIS_HOST", default="127.0.0.1", cast=str)
    REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
    REDIS_PASSWORD: str = config("REDIS_PASSWORD", default="", cast=str)
    REDIS_POOL_HEALTH_CHECK_INTERVAL: int = config("REDIS_POOL_HEALTH_CHECK_INTERVAL", default=30, cast=int)
    REDIS_POOL_MAX_CONNECTIONS: int = config("REDIS_POOL_MAX_CONNECTIONS", default=100, cast=int)
    REDIS_POOL_TIMEOUT: float = config("REDIS_POOL_MAX_CONNECTIONS", default=5.0, cast=int)
    REDIS_POOL_RETRY_ON_TIMEOUT: bool = config("REDIS_POOL_RETRY_ON_TIMEOUT", default=True, cast=bool)

    STORAGE_DOMAIN:str = config("STORAGE_DOMAIN", default="", cast=str)
    JWT_ALGORITHM:str = config("JWT_ALGORITHM", default="HS256", cast=str)
    SECRET_KEY: str = config("SECRET_KEY", default="", cast=str)
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", default="", cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = config(
        "BACKEND_CORS_ORIGINS",
        default="",
        cast=lambda v: [AnyHttpUrl(url.strip()) for url in Csv()(v)]
    )
    AGENT_IDS:list[str] = config(
        "AGENT_IDS",
        default="",
        cast=lambda v: [agent_id.strip() for agent_id in Csv()(v)]
    )
    EXTENSION_DIRS:list[str] = config(
        "EXTENSION_DIRS",
        default="",
        cast=lambda v: [edir.strip() for edir in Csv()(v)]
    )
    CHARACTERS_PATH:list[str] = config(
        "CHARACTERS_PATH",
        default="",
        cast=lambda v: [edir.strip() for edir in Csv()(v)]
    )
    COMMANDS_YAML_PATH: list[str] = config(
        "COMMANDS_YAML_PATH",
        default="",
        cast=lambda v: [edir.strip() for edir in Csv()(v)]
    )


    ENVIRONMENT: str = config("ENVIRONMENT",default="development",cast=str)



    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "production", "testing"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    def get_mongodb_settings(self) -> dict:
        return {
            "url": self.MONGODB_URL,
            "db_name": self.MONGODB_DB_NAME,
        }



settings = EnvSettings()