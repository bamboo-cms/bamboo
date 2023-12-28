import os
import sys
from pathlib import Path

basedir = Path(__file__).resolve().parent.parent.parent

default_data_dir = basedir / "data"

# SQLite URI compatible
prefix = "sqlite:///" if sys.platform.startswith("win") else "sqlite:////"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev key")
    BAMBOO_MEDIA_DIR = os.getenv("BAMBOO_MEDIA_DIR", str(default_data_dir / "media"))
    BAMBOO_SMALL_IMAGE_SUFFIX = os.getenv("BAMBOO_SMALL_IMAGE_SUFFIX", "_small")
    BAMBOO_SMALL_IMAGE_RATIO: float = float(os.getenv("BAMBOO_SMALL_IMAGE_RATIO", "0.3"))
    RQ_REDIS_URL = os.getenv("RQ_REDIS_URL", "redis://localhost:6379/0")


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + str(default_data_dir / "data-dev.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database
    RQ_CONNECTION_CLASS = "fakeredis.FakeStrictRedis"


class ProductionConfig(BaseConfig):
    RQ_REDIS_URL = os.getenv("RQ_REDIS_URL", "redis://redis:6379/0")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", prefix + str(default_data_dir / "data.db"))


config: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
