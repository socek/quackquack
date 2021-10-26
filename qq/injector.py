from contextlib import suppress
from functools import wraps
from inspect import BoundArguments
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


def injector_runner(method: Callable, application: Application = None):
    if getattr(method, QQ_PARAMETER, None):
        setattr(method, QQ_PARAMETER, application)
        return method

    @wraps(method)
    def wrapper(*args, **kwargs):
        injectors = list(get_injectors(method, args, kwargs))
        for name, injector in injectors:
            kwargs[name] = injector.start(application)

        runners = list(get_runners(method, args, kwargs))
        for name, runner in runners:
            kwargs[name] = injector_runner(runner, application)

        try:
            return method(*args, **kwargs)
        finally:
            for name, injector in reversed(injectors):
                injector.end()

    setattr(wrapper, QQ_PARAMETER, application)
    return wrapper


def InjectApplication(application: Application) -> Callable:
    def wrapper(method: Callable) -> Callable:
        """
        If function has injectors in the defaults of arguments, then init them.
        """
        runner = injector_runner(method, application)
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
        self.result = injector_runner(self.fun, application)(
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
    is_injector = isinstance(parameter._default, Injector)
    return is_injector and name not in bound_args.arguments


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
