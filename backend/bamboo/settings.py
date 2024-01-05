import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(data_dir) if (data_dir := os.getenv("DATA_DIR")) else BASE_DIR / "data"

# SQLite URI compatible
prefix = "sqlite:///" if sys.platform.startswith("win") else "sqlite:////"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev key")
    BAMBOO_MEDIA_DIR = os.getenv("BAMBOO_MEDIA_DIR", (DATA_DIR / "media").as_posix())
    BAMBOO_SMALL_IMAGE_SUFFIX = os.getenv("BAMBOO_SMALL_IMAGE_SUFFIX", "_small")
    BAMBOO_SMALL_IMAGE_RATIO: float = float(os.getenv("BAMBOO_SMALL_IMAGE_RATIO", "0.3"))
    RQ_REDIS_URL = os.getenv("RQ_REDIS_URL", "redis://localhost:6379/0")


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + (DATA_DIR / "data-dev.db").as_posix()


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database
    RQ_CONNECTION_CLASS = "fakeredis.FakeStrictRedis"


class ProductionConfig(BaseConfig):
    RQ_REDIS_URL = os.getenv("RQ_REDIS_URL", "redis://redis:6379/0")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", prefix + (DATA_DIR / "data.db").as_posix())


config: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
