from collections.abc import Iterable
from inspect import signature

from sapp.context_manager import LazyContextManager


class Decorator(object):
    def __init__(self, application, values=None):
        self.application = application
        self.values = values

    def get_unified_kwargs(self, fun, args, kwargs):
        return signature(fun).bind_partial(*args, **kwargs).arguments

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            kwargs = self.get_unified_kwargs(fun, args, kwargs)
            with LazyContextManager(self.application) as lazy_context:
                if not self.values:
                    # If no values passed to the decorator, it means we want to
                    # inject whole context
                    if "ctx" not in kwargs:
                        kwargs["ctx"] = lazy_context.context
                elif isinstance(self.values, str):
                    # If values passed to the decorator is a string, this mean
                    # we want to inject only one parametr from the context
                    parameter = self.values
                    if parameter not in kwargs:
                        kwargs[parameter] = lazy_context.get(parameter)
                elif isinstance(self.values, Iterable):
                    # If values passed to the decorator is a list, this mean
                    # we want to inject many parameteres from the context
                    for parameter in self.values:
                        if parameter not in kwargs:
                            kwargs[parameter] = lazy_context.get(parameter)
                else:
                    raise AttributeError(f"Wrong argument type: {self.values}!")
                return fun(**kwargs)

        return wrapper
