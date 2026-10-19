"""Journalisation structurée (JSON) partagée."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog


def configure_logging(
    level: str | None = None,
    json_output: bool | None = None,
) -> None:
    """Configurer la journalisation structurée globale.

    Paramètres pilotés par les variables d'environnement DOCUFLOW_LOG_LEVEL
    et DOCUFLOW_LOG_FORMAT (``json`` par défaut).
    """
    level = level or os.getenv("DOCUFLOW_LOG_LEVEL", "INFO").upper()
    if json_output is None:
        json_output = os.getenv("DOCUFLOW_LOG_FORMAT", "json").lower() == "json"

    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json_output:
        renderer: Any = structlog.processors.JSONRenderer(sort_keys=True)
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level, logging.INFO)
        ),
        processors=[*shared, renderer],
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, **initial: Any) -> structlog.typing.Logger:
    """Retourne un logger structuré nommé."""
    return structlog.get_logger(name).bind(**initial)
