from copy import copy
from functools import wraps
from inspect import BoundArguments
from inspect import iscoroutinefunction
from inspect import signature
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple

from qq.application import Application
from qq.types import BaseInjector

QQ_PARAMETER = "_qq_application"


class DefaultEmptyVar:
    pass


class ArgumentInitializer:
    """
    ArgumentInitializer makes sure that the injecotr will be started and
    ended after function is finished or raised an error.
    """

    def __init__(self, initializer, fun, args, kwargs):
        self.initializer = initializer
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.injectors = None

    def __enter__(self):
        kwargs = copy(self.kwargs)
        self.injectors = list(get_injectors(self.fun, self.args, self.kwargs))
        for name, injector in self.injectors:
            kwargs[name] = injector.start(self.initializer.application)

        initializers = list(get_initializers(self.fun, self.args, self.kwargs))
        for name, initializer in initializers:
            kwargs[name] = self.initializer.wrapper(initializer)
        return kwargs

    def __exit__(self, exc_type, exc_value, traceback):
        for name, injector in reversed(self.injectors):
            injector.end()


class ApplicationInitializer:
    def __init__(self, application: Application):
        self.application = application

    def __call__(self, fun: Callable) -> Callable:
        """
        If function has injectors in the defaults of arguments, then init them.
        """
        return wraps(fun)(self.wrapper(fun))

    def wrapper(self, fun: Callable):
        if getattr(fun, QQ_PARAMETER, None):
            setattr(fun, QQ_PARAMETER, self.application)
            return fun

        @wraps(fun)
        def qqfunction(*args, **kwargs):
            icm = ArgumentInitializer(self, fun, args, kwargs)
            with icm as kwargs:
                return fun(*args, **kwargs)

        @wraps(fun)
        async def qqcoroutine(*args, **kwargs):
            icm = ArgumentInitializer(self, fun, args, kwargs)
            with icm as kwargs:
                return await fun(*args, **kwargs)

        setattr(qqfunction, QQ_PARAMETER, self.application)
        setattr(qqcoroutine, QQ_PARAMETER, self.application)
        return qqcoroutine if iscoroutinefunction(fun) else qqfunction


def is_injector(parameter: Any, name: str, bound_args: BoundArguments):
    """
    Is parameter an injector and the value is not provided in the call.
    """
    value = (
        bound_args.arguments[name]
        if name in bound_args.arguments
        else parameter._default
    )
    return isinstance(value, BaseInjector)


def is_initializer(parameter: Any, name: str, bound_args: BoundArguments):
    """
    Is parameter an injector and the value is not provided in the call.
    """
    qq_application = getattr(parameter._default, QQ_PARAMETER, DefaultEmptyVar)
    is_injected = qq_application != DefaultEmptyVar
    return is_injected and name not in bound_args.arguments


def get_injectors(
    method: Callable,
    args: List,
    kwargs: Dict,
) -> Iterable[Tuple[str, Callable]]:
    """
    Generate list of iterators that was not overwrited by function's call args.
    """
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, parameter in sig._parameters.items():
        if is_injector(parameter, name, bound_args):
            yield name, parameter._default


def get_initializers(
    method: Callable,
    args: List,
    kwargs: Dict,
) -> Iterable[Tuple[str, Callable]]:
    """ """
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, parameter in sig._parameters.items():
        if is_initializer(parameter, name, bound_args):
            yield name, parameter._default
