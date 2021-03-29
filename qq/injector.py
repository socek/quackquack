import sys
from contextlib import suppress
from functools import wraps
from inspect import BoundArguments
from inspect import signature
from types import GeneratorType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple

from qq.context import Context


def is_injector_ready(parameter: Any, name: str, bound_args: BoundArguments):
    """
    Is parameter an injector and the value is not provided in the call.
    """
    is_injector = isinstance(parameter._default, Injector)
    return is_injector and name not in bound_args.arguments


def injectors(
    method: Callable, args: List, kwargs: Dict
) -> Iterable[Tuple[str, Callable]]:
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, parameter in sig._parameters.items():
        if is_injector_ready(parameter, name, bound_args):
            yield name, parameter._default


def InjectApplicationContext(method: Callable):
    @wraps(method)
    def wrapper(*args, **kwargs):
        injector_list = list(injectors(method, args, kwargs))
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
        self.application = application
        self.args = args
        self.kwargs = kwargs
        return self

    def start(self):
        context = Context(self.application).enter()
        self.result = self.fun(context, *self.args, **self.kwargs)
        if self._is_generator(self.result):
            return self.result.__next__()
        else:
            return self.result

    def end(self):
        if self._is_generator(self.result):
            with suppress(StopIteration):
                self.result.__next__()

    def _is_generator(self, obj):
        return isinstance(obj, GeneratorType)


class ContextManagerInjector(Injector):
    def __init__(self, application, *args, **kwargs):
        super().__init__(None)
        self.__call__(application, *args, **kwargs)

    def start(self):
        self.context = Context(self.application).enter()
        return self.__enter__(self.context, *self.args, **self.kwargs)

    def end(self):
        return self.__exit__(
            *sys.exc_info(),
            self.context,
            *self.args,
            **self.kwargs,
        )


@Injector
def SimpleInjector(context: Context, key: str):
    return context[key]
