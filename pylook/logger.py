import logging


class ColorFormatter(logging.Formatter):
    COLOR = dict(
        CRITICAL="95", ERROR="31", WARNING="33", INFO="32", DEBUG="34", TRACE=30
    )

    def format(self, record, color=True):
        if color:
            local_format = f"\033[{self.COLOR[record.levelname]}m{self._fmt}\033[0m"
        else:
            local_format = self._fmt
        return local_format.format(
            levelname=record.levelname,
            module=record.module,
            message=record.msg,
            funcName=record.funcName,
            asctime=self.formatTime(record),
        )


class PyLookHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statusbar = None
        self.setFormatter(
            ColorFormatter(
                "{levelname} {asctime} {module}.{funcName} : {message}", style="{"
            )
        )

    def emit(self, record):
        super().emit(record)
        if self.statusbar is not None:
            self.statusbar.showMessage(self.formatter.format(record, color=False))

    def set_statusbar(self, statusbar):
        self.statusbar = statusbar


def start_logger():
    TRACE = 5
    logging.addLevelName(TRACE, "TRACE")
    logger = logging.getLogger("pylook")
    logger.addHandler(PyLookHandler())
    logger.trace = lambda msg, *args, **kwargs: logger._log(TRACE, msg, args, **kwargs)
    return logger
