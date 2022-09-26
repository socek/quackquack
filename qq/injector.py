from contextlib import suppress
from copy import copy
from functools import wraps
from inspect import BoundArguments
from inspect import iscoroutinefunction
from inspect import signature
from sys import exc_info
from types import GeneratorType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple

from qq.application import Application
from qq.context import Context
from qq.errors import InjectorNotInicialized

QQ_PARAMETER = "_qq_application"


class DefaultEmptyVar:
    pass


def parse_parameters(application, method, args, kwargs):
    kwargs = copy(kwargs)
    injectors = list(get_injectors(method, args, kwargs))
    for name, injector in injectors:
        kwargs[name] = injector.start(application)

    runners = list(get_runners(method, args, kwargs))
    for name, runner in runners:
        kwargs[name] = application_runner(runner, application)
    return kwargs, injectors


class InjectorsContextManager:
    def __init__(self, application, method, args, kwargs):
        self.application = application
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        kwargs, self.injectors = parse_parameters(
            self.application,
            self.method,
            self.args,
            self.kwargs,
        )
        return kwargs

    def __exit__(self, exc_type, exc_value, traceback):
        for name, injector in reversed(self.injectors):
            injector.end()


def application_runner(
    method: Callable,
    application: Application = None,
):
    if getattr(method, QQ_PARAMETER, None):
        setattr(method, QQ_PARAMETER, application)
        return method

    @wraps(method)
    def qqfunction(*args, **kwargs):
        with InjectorsContextManager(
            application, method, args, kwargs
        ) as kwargs:
            return method(*args, **kwargs)

    @wraps(method)
    async def qqcoroutine(*args, **kwargs):
        with InjectorsContextManager(
            application, method, args, kwargs
        ) as kwargs:
            return await method(*args, **kwargs)

    setattr(qqfunction, QQ_PARAMETER, application)
    setattr(qqcoroutine, QQ_PARAMETER, application)
    return qqcoroutine if iscoroutinefunction(method) else qqfunction


def CreateApplicationDecorator(application: Application) -> Callable:
    def wrapper(method: Callable) -> Callable:
        """
        If function has injectors in the defaults of arguments, then init them.
        """
        runner = application_runner(method, application)
        return wraps(method)(runner)

    return wrapper


class Injector:
    def __init__(self, fun):
        self.fun = fun
        self._initialized = False

    def __call__(self, *args, **kwargs):
        return self.__class__(self.fun).init(*args, **kwargs)

    def init(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._initialized = True
        return self

    def start(self, application: Application):
        if not self._initialized:
            raise InjectorNotInicialized()
        self.context = Context(application)
        self.entered = self.context.__enter__()
        self.result = application_runner(self.fun, application)(
            self.entered, *self.args, **self.kwargs
        )
        if _is_generator(self.result):
            return self.result.__next__()
        else:
            return self.result

    def end(self):
        if _is_generator(self.result):
            with suppress(StopIteration):
                self.result.__next__()
        self.context.__exit__(*exc_info())


class ContextManagerInjector(Injector):
    def __init__(self, *args, **kwargs):
        super().__init__(None)
        self.init(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self  # pragma: no cover

    def start(self, application: Application):
        self.context = Context(application)
        self.entered = self.context.__enter__()
        return self.__enter__(self.entered, *self.args, **self.kwargs)

    def end(self):
        self.__exit__(
            *exc_info(),
            self.entered,
            *self.args,
            **self.kwargs,
        )
        self.context.__exit__(*exc_info())


@Injector
def SimpleInjector(context: Context, key: str):
    return context[key]


def is_injector_ready(parameter: Any, name: str, bound_args: BoundArguments):
    """
    Is parameter an injector and the value is not provided in the call.
    """
    value = (
        bound_args.arguments[name]
        if name in bound_args.arguments
        else parameter._default
    )
    return isinstance(value, Injector)


def is_injected_ready(parameter: Any, name: str, bound_args: BoundArguments):
    """
    Is parameter an injector and the value is not provided in the call.
    """
    qq_application = getattr(parameter._default, QQ_PARAMETER, DefaultEmptyVar)
    is_injected = qq_application != DefaultEmptyVar
    return is_injected and name not in bound_args.arguments


def get_injectors(
    method: Callable, args: List, kwargs: Dict
) -> Iterable[Tuple[str, Callable]]:
    """
    Generate list of iterators that was not overwrited by function's call args.
    """
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, parameter in sig._parameters.items():
        if is_injector_ready(parameter, name, bound_args):
            yield name, parameter._default


def get_runners(
    method: Callable, args: List, kwargs: Dict
) -> Iterable[Tuple[str, Callable]]:
    """ """
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, parameter in sig._parameters.items():
        if is_injected_ready(parameter, name, bound_args):
            yield name, parameter._default


def _is_generator(obj):
    return isinstance(obj, GeneratorType)
