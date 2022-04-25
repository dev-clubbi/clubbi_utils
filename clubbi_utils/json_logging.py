from typing import Any
from .logging import logger, LogLevelEnum
from clubbi_utils import json
from typing import Callable
import logging


class JsonLogger:
    def __init__(self, logger:logging.Logger):
        self.logger = logger
        setattr(self, "fatal", self._log(LogLevelEnum.fatal))
        setattr(self, "error", self._log(LogLevelEnum.error))
        setattr(self, "warning", self._log(LogLevelEnum.warning))
        setattr(self, "info", self._log(LogLevelEnum.info))
        setattr(self, "debug", self._log(LogLevelEnum.debug))

    def log(self, log_level: LogLevelEnum, workflow: str, message: str, **kwargs: Any) -> None:
        payload = dict(
            workflow=workflow,
            message=message,
            level=log_level,
            **kwargs,
        )
        self.logger.log(level=log_level.to_python_log_level(), msg=json.dumps(payload))

    def _log(self, log_level: LogLevelEnum) -> Callable:
        return lambda workflow, message, **kwargs: self.log(log_level, workflow, message, **kwargs)

    def fatal(self, workflow: str, message: str, **kwargs: Any) -> None:
        pass

    def error(self, workflow: str, message: str, **kwargs: Any) -> None:
        pass

    def warning(self, workflow: str, message: str, **kwargs: Any) -> None:
        pass

    def info(self, workflow: str, message: str, **kwargs: Any) -> None:
        pass

    def debug(self, workflow: str, message: str, **kwargs: Any) -> None:
        pass


jlogger = JsonLogger(logger)
