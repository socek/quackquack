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


def is_context_manager(obj):
    try:
        issub = issubclass(obj, ContextManagerInjector)
    except TypeError:
        issub = False

    return issub or isinstance(obj, ContextManagerInjector)


def InjectApplicationContext(method: Callable):
    @wraps(method)
    def wrapper(*args, **kwargs):
        contexts = []
        injectorsObjs = []
        for name, injector in injectors(method, args, kwargs):
            context = Context(injector._injector["application"])
            iArgs = injector._injector["args"]
            iKwargs = injector._injector["kwargs"]
            entered = context.enter()
            injectorObj = injector(entered, *iArgs, **iKwargs)
            if isinstance(injectorObj, GeneratorType):
                injectorsObjs.append(injectorObj)
                kwargs[name] = injectorObj.__next__()
            elif is_context_manager(injectorObj):
                injectorsObjs.append(injectorObj)
                kwargs[name] = injectorObj.__enter__()
            else:
                kwargs[name] = injectorObj
            contexts.append(context)
        try:
            return method(*args, **kwargs)
        finally:
            for injector in reversed(injectorsObjs):
                if is_context_manager(injector):
                    injector.__exit__(*sys.exc_info())
                else:
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


class ContextManagerInjector:
    def __init__(self, appliication, *args, **kwargs):
        self._injector = {
            "application": appliication,
            "args": args,
            "kwargs": kwargs,
        }

    def __call__(self, context, *args, **kwargs):
        self.context = context
        return self

    def __enter__(self):
        return self.enter(
            self.context, *self._injector["args"], **self._injector["kwargs"]
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit(
            exc_type,
            exc_value,
            traceback,
            self.context,
            *self._injector["args"],
            **self._injector["kwargs"],
        )

    def enter(self, context):
        pass  # pragma: no cover

    def exit(self, exc_type, exc_value, traceback, context):
        pass  # pragma: no cover


@Injector
def SimpleInjector(context: Context, key: str):
    return context[key]
