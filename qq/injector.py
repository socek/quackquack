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
    injector = getattr(parameter._default, "_injector", False)
    return injector and name not in bound_args.arguments


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
        contexts = []
        generators = []
        for name, injector in injectors(method, args, kwargs):
            context = Context(injector._injector["application"])
            injectorObj = injector(
                context.enter(),
                *injector._injector["args"],
                **injector._injector["kwargs"],
            )
            if isinstance(injectorObj, GeneratorType):
                generators.append(injectorObj)
                kwargs[name] = injectorObj.__next__()
            else:
                kwargs[name] = injectorObj
            contexts.append(context)
        try:
            return method(*args, **kwargs)
        finally:
            for injector in reversed(generators):
                with suppress(StopIteration):
                    injector.__next__()
            for context in reversed(contexts):
                context.exit(*sys.exc_info())

    return wrapper


def Injector(method: Callable):
    @wraps(method)
    def wrapper(appliication, *args, **kwargs):
        method._injector = {
            "application": appliication,
            "args": args,
            "kwargs": kwargs,
        }
        return method

    return wrapper


@Injector
def SimpleInjector(context: Context, key: str):
    return context[key]
