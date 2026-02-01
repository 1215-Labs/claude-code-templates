"""
Lightweight logging utility for Claude Code hooks and tools.

Zero dependencies - stdlib only for fast imports.

Usage:
    from utils.logging import get_logger
    log = get_logger(__name__)

    log.info("Hook executed", decision="approve", branch="main")
    log.error("Validation failed", file="src/api.ts", errors=3)
"""

import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Add extra fields passed via log.info("msg", key=value)
        extra = getattr(record, "_extra", None)
        if extra:
            log_data.update(extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exc"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class ConsoleFormatter(logging.Formatter):
    """Compact formatter for console/stderr output."""

    LEVELS = {"DEBUG": "DBG", "INFO": "INF", "WARNING": "WRN", "ERROR": "ERR"}

    def format(self, record: logging.LogRecord) -> str:
        level = self.LEVELS.get(record.levelname, record.levelname[:3])
        ts = datetime.now().strftime("%H:%M:%S")
        msg = record.getMessage()

        # Append extra fields inline
        extra_data = getattr(record, "_extra", None)
        extra = ""
        if extra_data:
            extra = " " + " ".join(f"{k}={v}" for k, v in extra_data.items())

        return f"{ts} {level} [{record.name}] {msg}{extra}"


class StructuredLogger(logging.Logger):
    """Logger that accepts keyword arguments as structured data."""

    def _log_with_extra(
        self, level: int, msg: str, args: tuple, exc_info: Any = None, **kwargs: Any
    ) -> None:
        extra = {"_extra": kwargs} if kwargs else {}
        super()._log(level, msg, args, exc_info=exc_info, extra=extra)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(logging.DEBUG):
            self._log_with_extra(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(logging.INFO):
            self._log_with_extra(logging.INFO, msg, args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(logging.WARNING):
            self._log_with_extra(logging.WARNING, msg, args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(logging.ERROR):
            self._log_with_extra(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs["exc_info"] = kwargs.get("exc_info", sys.exc_info())
        self.error(msg, *args, **kwargs)


# Register custom logger class
logging.setLoggerClass(StructuredLogger)

# Module-level state
_initialized = False
_log_dir: Path | None = None


def _get_log_dir() -> Path:
    """Get or create log directory."""
    global _log_dir
    if _log_dir is None:
        _log_dir = Path.home() / ".claude" / "logs"
        _log_dir.mkdir(parents=True, exist_ok=True)
    return _log_dir


def _init_root_logger() -> None:
    """Initialize root logger with handlers."""
    global _initialized
    if _initialized:
        return

    root = logging.getLogger("claude")
    root.setLevel(logging.DEBUG)

    # File handler - JSON structured logs
    log_file = _get_log_dir() / "hooks.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(StructuredFormatter())
    root.addHandler(file_handler)

    # Console handler - compact format, only warnings+
    # Disabled by default to avoid polluting hook output
    if os.environ.get("CLAUDE_LOG_CONSOLE"):
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(ConsoleFormatter())
        root.addHandler(console_handler)

    _initialized = True


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        StructuredLogger with JSON file output

    Example:
        log = get_logger(__name__)
        log.info("Hook executed", decision="approve", duration_ms=45)
    """
    _init_root_logger()

    # Create child logger under 'claude' namespace
    if not name.startswith("claude."):
        name = f"claude.{name}"

    return logging.getLogger(name)  # type: ignore


# Convenience shortcuts for quick logging without creating a logger
def _quick_log(level: int, msg: str, **kwargs: Any) -> None:
    """Quick log without explicit logger creation."""
    log = get_logger("quick")
    log._log_with_extra(level, msg, (), **kwargs)


def debug(msg: str, **kwargs: Any) -> None:
    _quick_log(logging.DEBUG, msg, **kwargs)


def info(msg: str, **kwargs: Any) -> None:
    _quick_log(logging.INFO, msg, **kwargs)


def warning(msg: str, **kwargs: Any) -> None:
    _quick_log(logging.WARNING, msg, **kwargs)


def error(msg: str, **kwargs: Any) -> None:
    _quick_log(logging.ERROR, msg, **kwargs)


# Specialized logging functions for common patterns
def hook(name: str, decision: str, **kwargs: Any) -> None:
    """Log hook execution."""
    log = get_logger("hooks")
    log.info(f"hook:{name}", decision=decision, **kwargs)


def audit(action: str, **kwargs: Any) -> None:
    """Log auditable action (fork terminal, file ops, etc)."""
    log = get_logger("audit")
    log.info(action, **kwargs)


def metric(name: str, value: float = 1, **kwargs: Any) -> None:
    """Log a metric for later aggregation."""
    log = get_logger("metrics")
    log.info(name, value=value, **kwargs)


@contextmanager
def timed(name: str, **kwargs: Any) -> Generator[dict[str, Any], None, None]:
    """
    Context manager for timing operations.

    Usage:
        with timed("database_query", table="users") as ctx:
            result = db.query()
        # Automatically logs: "database_query" with duration_ms

        # Access timing in context:
        with timed("operation") as ctx:
            do_work()
        print(f"Took {ctx['duration_ms']}ms")
    """
    ctx: dict[str, Any] = {"start": time.perf_counter()}
    try:
        yield ctx
    finally:
        ctx["duration_ms"] = round((time.perf_counter() - ctx["start"]) * 1000, 2)
        log = get_logger("timing")
        log.info(name, duration_ms=ctx["duration_ms"], **kwargs)


def timed_hook(name: str, decision: str, **kwargs: Any) -> "TimedHook":
    """
    Context manager for timing hook execution.

    Usage:
        with timed_hook("session-init", decision="approve", branch="main") as h:
            # do hook work
            h.set(project_types=["python"])  # add more data
    """
    return TimedHook(name, decision, **kwargs)


class TimedHook:
    """Context manager for timed hook logging."""

    def __init__(self, name: str, decision: str, **kwargs: Any):
        self.name = name
        self.decision = decision
        self.kwargs = kwargs
        self.start = 0.0

    def set(self, **kwargs: Any) -> None:
        """Add additional data to be logged."""
        self.kwargs.update(kwargs)

    def __enter__(self) -> "TimedHook":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        duration_ms = round((time.perf_counter() - self.start) * 1000, 2)
        hook(self.name, self.decision, duration_ms=duration_ms, **self.kwargs)
