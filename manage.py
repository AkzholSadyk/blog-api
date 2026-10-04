#!/usr/bin/env python
import os
import sys
from pathlib import Path

from decouple import Config, RepositoryEnv


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "settings" / ".env"

config = Config(RepositoryEnv(str(ENV_FILE)))

ENVIRONMENT = config("BLOG_ENV_ID", default="local")

SETTINGS_MODULES = {
    "local": "settings.env.local",
    "prod": "settings.env.prod",
}

settings_module = SETTINGS_MODULES.get(ENVIRONMENT)

if settings_module is None:
    raise ValueError(
        f"Unsupported BLOG_ENV_ID: {ENVIRONMENT}. "
        f"Expected one of: {', '.join(SETTINGS_MODULES)}."
    )


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Make sure it is installed.") from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
