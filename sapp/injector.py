from functools import wraps
from inspect import BoundArguments
from inspect import Signature
from inspect import signature
from typing import Any
from typing import Callable
from typing import ContextManager as ContextManagerType

from sapp.configurator import Configurator
from sapp.context_manager import ContextManager


class ArgsInjector:
    def __init__(self, name: str, getvalue: Callable[[], Any]):
        self.name = name
        self.getvalue = getvalue

    def _is_argument_not_set(self, sig: Signature, bound_args: BoundArguments):
        default_value = sig.parameters[self.name].default
        value = bound_args.arguments.get(self.name)
        return default_value == value

    def __call__(self, method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            sig = signature(method)
            bound_args = sig.bind_partial(*args, **kwargs)
            if self._is_argument_not_set(sig, bound_args):
                return self.run_method(method, args, kwargs)
            return method(*args, **kwargs)

        return wrapper

    def run_method(self, method, args, kwargs):
        kwargs[self.name] = self.getvalue()
        return method(*args, **kwargs)


class ContextArgsInjector(ArgsInjector):
    def __init__(
        self,
        name: str,
        getvalue: Callable[[Any], Any],
        context: ContextManagerType,
    ):
        super().__init__(name, getvalue)
        self.context = context

    def run_method(self, method, args, kwargs):
        with self.context as context:
            kwargs[self.name] = self.getvalue(context)
        return method(*args, **kwargs)


class ApplicationArgsInjector(ArgsInjector):
    def __init__(
        self,
        name: str,
        application: Configurator,
        getvalue: Callable[[Any], Any] = None,
    ):
        getvalue = getvalue or (lambda ctx: getattr(ctx, name))
        super().__init__(name, getvalue)
        self.application = application

    def run_method(self, method, args, kwargs):
        with ContextManager(self.application) as context:
            kwargs[self.name] = self.getvalue(context)
        return method(*args, **kwargs)
