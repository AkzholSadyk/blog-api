from pathlib import Path

from decouple import Config, RepositoryEnv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "settings" / ".env"

config = Config(RepositoryEnv(str(ENV_FILE)))

BLOG_ENV_ID = config("BLOG_ENV_ID", default="local")
BLOG_SECRET_KEY = config("BLOG_SECRET_KEY")
BLOG_DEBUG = config("BLOG_DEBUG", cast=bool, default=False)
BLOG_ALLOWED_HOSTS = config(
    "BLOG_ALLOWED_HOSTS",
    cast=lambda value: [host.strip() for host in value.split(",")],
    default="127.0.0.1,localhost",
)
