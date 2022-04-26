import enum
from pydantic import BaseSettings
import logging


class LogLevelEnum(enum.Enum):
    fatal = "FATAL"
    error = "ERROR"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"
    notset = "NOTSET"

    def to_python_log_level(self) -> int:
        return {
            LogLevelEnum.fatal: logging.FATAL,
            LogLevelEnum.error: logging.ERROR,
            LogLevelEnum.warning: logging.WARNING,
            LogLevelEnum.info: logging.INFO,
            LogLevelEnum.debug: logging.DEBUG,
            LogLevelEnum.notset: logging.NOTSET,
        }.get(self, logging.INFO)


class LoggingSettings(BaseSettings):
    log_level: LogLevelEnum = LogLevelEnum.info


log_level = LoggingSettings().log_level.to_python_log_level()
if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(log_level)
else:
    logging.basicConfig(level=log_level)

logger = logging.getLogger()
