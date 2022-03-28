from .logging import logger as _logger

_logger.warn("Deprecation warning: import from clubbi_utils.logging instead of clubbi_utils.logger")
logger = _logger
