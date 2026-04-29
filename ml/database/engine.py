from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ml.config.settings import ensure_project_dirs, settings


def get_engine(echo: bool = False) -> Engine:
    ensure_project_dirs()
    kwargs = {"echo": echo, "future": True}
    if settings.database_url.startswith("mssql+pyodbc"):
        kwargs["fast_executemany"] = True
        kwargs["pool_pre_ping"] = True
    return create_engine(settings.database_url, **kwargs)
