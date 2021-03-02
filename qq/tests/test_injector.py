from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.injector import ApplicationArgsInjector
from qq.injector import ArgsInjector
from qq.injector import ContextArgsInjector


def testfunction(arg1=1, arg2=2, arg3=None, arg4=4):
    return arg1, arg2, arg3, arg4


first = ArgsInjector("arg3", lambda: sentinel.arg)(testfunction)


class TestInjectors:
    @fixture
    def ctx(self):
        return MagicMock()

    @fixture
    def ctxfun(self, ctx):
        return ContextArgsInjector("arg3", lambda ctx: ctx, ctx)(testfunction)

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def appfun(self, app):
        return ApplicationArgsInjector("arg3", app)(testfunction)

    def test_1(self):
        assert first(arg3=sentinel.kwarg) == (1, 2, sentinel.kwarg, 4)

    def test_2(self):
        assert first(10, 11, 12, 13) == (10, 11, 12, 13)

    def test_3(self):
        assert first() == (1, 2, sentinel.arg, 4)

    def test_4(self, ctxfun, ctx):
        assert ctxfun(arg3=sentinel.kwarg) == (1, 2, sentinel.kwarg, 4)

    def test_5(self, ctxfun, ctx):
        assert ctxfun(10, 11, 12, 13) == (10, 11, 12, 13)

    def test_6(self, ctxfun, ctx):
        assert ctxfun() == (1, 2, ctx.__enter__.return_value, 4)

    def test_7(self, appfun, app):
        assert appfun(arg3=sentinel.kwarg) == (1, 2, sentinel.kwarg, 4)

    def test_8(self, appfun, app):
        assert appfun(10, 11, 12, 13) == (10, 11, 12, 13)

    def test_9(self, appfun, app):
        assert appfun() == (1, 2, app._enter_context.return_value.arg3, 4)
