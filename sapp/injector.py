import sys
from functools import wraps
from inspect import signature
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple

from sapp.context import Context


def _injectors(
    method: Callable, args: List, kwargs: Dict
) -> Iterable[Tuple[str, Callable]]:
    sig = signature(method)
    bound_args = sig.bind_partial(*args, **kwargs)

    for name, value in sig._parameters.items():
        if getattr(value._default, "_injectable", False):
            if name not in bound_args.arguments:
                yield name, value._default


def InitalizeInjectors(method: Callable):
    @wraps(method)
    def wrapper(*args, **kwargs):
        contexts = []
        for name, injector in _injectors(method, args, kwargs):
            context = Context(injector._appliication).start()
            kwargs[name] = injector(context)
            contexts.append(context)
        try:
            method(*args, **kwargs)
        finally:
            for context in reversed(contexts):
                context.exit(*sys.exc_info())

    return wrapper


def Injector(method: Callable):
    @wraps(method)
    def wrapper(appliication):
        method._appliication = appliication
        method._injectable = True
        return method

    return wrapper
