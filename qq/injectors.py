from copy import copy
from functools import wraps
from inspect import signature
from typing import Any
from typing import Callable

from qq.application import Application
from qq.context import Context


class Inicjator:
    def init(self, context, arguments):
        self.context = context
        self.arguments = arguments

    def start(self) -> Any:
        ...

    def finish(self, er=None):
        ...


class ContextInicjator(Inicjator):
    def __init__(self, key: str):
        self.key = key

    def start(self):
        return self.context[self.key]


class QQFunctionWrapper(Inicjator):
    def __init__(self, fun: Callable):
        self.application = None
        self.configuration = None
        self.fun = fun

    def init(self, context: Context, arguments: dict[str, Any]):
        self.application = context.application

    def start(self):
        return self

    def __call__(self, *args, **kwargs):
        assert self.configuration
        assert self.application

        sig = signature(self.fun)
        arguments = sig.bind_partial(*args, **kwargs).arguments
        inicjators = []
        with Context(self.application) as context:
            for key in sig.parameters.keys():
                inicjator = self.configuration.get(key)
                if key not in arguments and inicjator:
                    inicjator = copy(inicjator)
                    inicjators.append(inicjator)
                    inicjator.init(context, arguments)
                    arguments[key] = inicjator.start()

        try:
            result = self.fun(**arguments)
        except Exception as er:
            for conf in reversed(inicjators):
                conf.finish(er)
            raise

        for conf in reversed(inicjators):
            conf.finish()

        return result


class ArgsInjector:
    def __init__(
        self,
        application: Application | None = None,
        configuration: dict[str, Inicjator | Callable] | None = None,
    ):
        self.application = application
        self.configuration = configuration

    def __call__(self, fun: Callable | QQFunctionWrapper) -> Callable:
        """
        If function has injectors in the defaults of arguments, then init them.
        """
        fun = (
            fun
            if isinstance(fun, QQFunctionWrapper)
            else wraps(fun)(QQFunctionWrapper(fun))
        )
        assert isinstance(fun, QQFunctionWrapper)

        if self.application:
            fun.application = self.application
        if self.configuration:
            fun.configuration = self.configuration
        return fun
