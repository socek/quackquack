class QQError(RuntimeError):
    pass


class ApplicationNotStartedError(QQError):
    pass


class AlreadyStartedError(QQError):
    pass


class PluginLacksOfKeyError(QQError):
    pass


class WrongKeyForPluginError(QQError):
    pass


class PluginKeyAlreadyDefinedError(QQError):
    pass
