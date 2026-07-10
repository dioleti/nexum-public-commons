from .errors import NexumError
from .errors import __all__ as errors_all
from .logging import setup_logging

__all__ = [
  *errors_all,
  "setup_logging",
]

import logging

if not logging.getLogger().handlers:
  setup_logging()
