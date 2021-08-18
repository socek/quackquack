class QQError(RuntimeError):
    pass


class ApplicationNotStartedError(QQError):
    pass


class AlreadyStartedError(QQError):
    pass
