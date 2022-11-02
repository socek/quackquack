from contextlib import suppress
from sys import exc_info
from types import GeneratorType

from qq.application import Application
from qq.context import Context
from qq.errors import InjectorNotInicialized
from qq.initializers import ApplicationInitializer
from qq.types import BaseInjector


class Injector(BaseInjector):
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
        self.result = ApplicationInitializer(application)(self.fun)(
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


def _is_generator(obj):
    return isinstance(obj, GeneratorType)
