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

from qq.context import Context


def InitializeInjectors(method: Callable):
    """
    If function has injectors in the defaults of arguments, then start them.
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        injector_list = list(get_injectors_from_function(method, args, kwargs))
        for name, injector in injector_list:
            kwargs[name] = injector.start()

        try:
            return method(*args, **kwargs)
        finally:
            for name, injector in reversed(injector_list):
                injector.end()

    return wrapper


class Injector:
    def __init__(self, fun):
        self.fun = fun

    def __call__(self, application, *args, **kwargs):
        return self.__class__(self.fun).init(application, *args, **kwargs)

    def init(self, application, *args, **kwargs):
        self.application = application
        self.args = args
        self.kwargs = kwargs
        return self

    def start(self):
        self.context = Context(self.application)
        self.entered = self.context.__enter__()
        self.result = self.fun(self.entered, *self.args, **self.kwargs)
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
    def __init__(self, application, *args, **kwargs):
        super().__init__(None)
        self.init(application, *args, **kwargs)

    def __call__(self, application, *args, **kwargs):
        return self  # pragma: no cover

    def start(self):
        self.context = Context(self.application)
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


def get_injectors_from_function(
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


def _is_generator(obj):
    return isinstance(obj, GeneratorType)
