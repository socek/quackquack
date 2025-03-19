from copy import copy
from functools import update_wrapper
from functools import wraps
from inspect import iscoroutinefunction
from inspect import signature
from typing import Any
from typing import Callable

from qq.application import Application
from qq.context import Context


class Inicjator:
    def init(self, context, arguments):
        self.context = context
        self.arguments = arguments

    def start(self) -> Any: ...  # pragma: no cover
    def finish(self, er=None): ...  # pragma: no cover


class ContextInicjator(Inicjator):
    def __init__(self, key: str):
        self.key = key

    def start(self):
        return self.context[self.key]


class FunctionWrapper:
    def __init__(self, fun: Callable):
        self.application = None
        self.inicjators = {}
        self.fun = fun
        update_wrapper(self, fun)

    def __call__(self, *args, **kwargs):
        sig = signature(self.fun)
        arguments = sig.bind_partial(*args, **kwargs).arguments
        inicjators = []
        with Context(self.application) as context:
            for key in sig.parameters.keys():
                inicjator = self.inicjators.get(key)
                if key not in arguments and inicjator:
                    inicjator = copy(inicjator)
                    inicjators.append(inicjator)
                    inicjator.init(context, arguments)
                    arguments[key] = inicjator.start()

        try:
            error = None
            result = self.fun(**arguments)
        except Exception as er:
            error = er
            raise
        finally:
            for injector in reversed(inicjators):
                injector.finish(error)

        return result

    def set_application(self, application):
        self.application = application

    def set_injector(self, key, injector):
        self.inicjators[key] = injector

    def __repr__(self):
        return repr(self.fun)


class SetApplication:
    def __init__(self, application):
        self.application = application

    def __call__(self, fun):
        if not isinstance(fun, FunctionWrapper):
            fun = FunctionWrapper(fun)
        fun.set_application(self.application)
        return fun


class SetInicjator:
    def __init__(self, key, inicjator):
        self.key = key
        self.inicjator = inicjator

    def __call__(self, fun):
        if not isinstance(fun, FunctionWrapper):
            fun = FunctionWrapper(fun)
        fun.set_injector(self.key, self.inicjator)
        return fun
