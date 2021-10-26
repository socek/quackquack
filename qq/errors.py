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


class InjectorNotInicialized(QQError):
    """
    This error means the injector was not properly created. Probaly, used:

    def fun(param = Injector):
        pass

    Instead of:

    def fun(param = Injector()):
        pass
    """

    def __init__(self):
        super().__init__(self.__doc__)
