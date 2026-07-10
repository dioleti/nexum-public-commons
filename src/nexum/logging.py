import logging
import json
import os
from datetime import datetime

from dotenv import load_dotenv

try:
    from ddtrace import tracer as dd_tracer
except Exception:
    dd_tracer = None

try:
    import elasticapm
    from elasticapm.traces import execution_context
except Exception:
    elasticapm = None

COLORS = {
    "DEBUG": "\033[36m",   # Cyan
    "INFO": "\033[32m",    # Green
    "WARNING": "\033[33m", # Yellow
    "ERROR": "\033[31m",   # Red
    "CRITICAL": "\033[41m" # Red background
}
RESET = "\033[0m"

class NexumLocalFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}][Nexum]"

        color = COLORS.get(record.levelname, "")
        level = f"{color}{record.levelname}{RESET}"

        message = super().format(record)
        return f"{prefix} {level}: {message}"


class NexumDatadogFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "prefix": "Nexum",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        if dd_tracer:
            span = dd_tracer.current_span()
            if span:
                log_entry["dd.trace_id"] = span.trace_id
                log_entry["dd.span_id"] = span.span_id

        return json.dumps(log_entry)


class NexumElasticFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.utcnow().isoformat() + "Z"

        log_entry = {
            "@timestamp": timestamp,
            "service": "nexum",
            "log.level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        if elasticapm:
            trace_id = execution_context.get_trace_id()
            transaction_id = execution_context.get_transaction_id()

            if trace_id:
                log_entry["trace.id"] = trace_id
            if transaction_id:
                log_entry["transaction.id"] = transaction_id

        return json.dumps(log_entry)


def setup_logging():
    load_dotenv()

    mode = os.getenv("NEXUM_LOG_MODE", "LOCAL").upper()
    user_level = os.getenv("LOG_LEVEL")

    handler = logging.StreamHandler()

    if user_level:
        level = user_level.upper()
    else:
        if mode == "LOCAL":
            level = "DEBUG"
        else:
            level = "INFO"

    if mode == "LOCAL":
        handler.setFormatter(NexumLocalFormatter("%(message)s"))

    elif mode == "DATADOG":
        handler.setFormatter(NexumDatadogFormatter())

    elif mode == "ELASTIC":
        handler.setFormatter(NexumElasticFormatter())

    else:
        handler.setFormatter(NexumLocalFormatter("%(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
