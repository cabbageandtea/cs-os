from __future__ import annotations

import logging
import os

from pythonjsonlogger import jsonlogger

_DEFAULT_SERVICE = "cs-os"
_DEFAULT_ENV = "production"
_DEFAULT_LOG_LEVEL = "INFO"


class _DatadogContextFilter(logging.Filter):
    def __init__(self, service: str, env: str) -> None:
        super().__init__()
        self._service = service
        self._env = env

    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__.setdefault("dd.service", self._service)
        record.__dict__.setdefault("dd.env", self._env)
        return True


def _log_level() -> int:
    level_name = (os.getenv("LOG_LEVEL") or _DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, level_name, logging.INFO)


def setup_logging() -> None:
    service = (os.getenv("DD_SERVICE") or _DEFAULT_SERVICE).strip() or _DEFAULT_SERVICE
    env = (os.getenv("DD_ENV") or _DEFAULT_ENV).strip() or _DEFAULT_ENV
    level = _log_level()

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(dd.service)s %(dd.env)s"
    )

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.addFilter(_DatadogContextFilter(service=service, env=env))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.propagate = False
