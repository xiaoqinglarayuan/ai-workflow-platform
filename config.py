from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Only define the one “broker” env var in HOST:PORT format
    REDIS_BROKER: str = Field(
        "localhost:6379",
        description="Redis broker in host:port format, e.g. localhost:6379",
    )

    WORKER_QUEUE: str = Field(
        "fastapi-app-queue-1",
        description="Redis queue to listen to for jobs",
    )

    JOBS_DB: str = Field(
        "database/jobs.db",
        description="SQLAlchemy database URL for jobs",
    )

    # These two will be filled in by our validator
    redis_host: str
    redis_port: int

    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_API_KEY: str = ""        # 真 key 从环境变量 / .env 读,别写死在这
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:test1234@localhost:5432/aiwf"   # ← 加这行

    # This runs before any other parsing, so we can split out host & port
    @model_validator(mode="before")
    @classmethod
    def _split_redis_broker(cls, values):
        broker = values.get("REDIS_BROKER", "localhost:6379")
        host, port_str = broker.split(":", 1)
        # overwrite/add our computed fields
        values["redis_host"] = host
        values["redis_port"] = int(port_str)
        return values
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
    # 把异步驱动换成同步驱动,供建表/同步会话用
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")

    # pydantic v2 way to point to an .env file
 
    


@lru_cache
def get_settings() -> Settings:
    return Settings()
