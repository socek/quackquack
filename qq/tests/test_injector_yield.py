from contextvars import ContextVar
from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.context import Context
from qq.injector import ContextManagerInjector
from qq.injector import InjectApplication
from qq.injector import Injector


class Fixtures:
    @fixture
    def mplugin(self):
        mock = MagicMock()
        mock.enter.return_value = sentinel.name
        return mock

    @fixture
    def mapp(self, mplugin):
        mock = MagicMock()
        mock.is_started = True
        mock.context = ContextVar("testing")
        mock.plugins = {
            "name": mplugin,
        }
        return mock

    @fixture
    def data(self):
        return {
            "name": 0,
        }

    @fixture
    def context(self, mapp):
        return Context(mapp)


class TestReturnInjector(Fixtures):
    @fixture
    def exampleinjector(self, data):
        @Injector
        def fun(context, key):
            data[key] = 1
            return context[key]

        return fun

    @fixture
    def examplefun(self, exampleinjector, mapp, data):
        def fun(obj=exampleinjector("name")):
            assert data["name"] == 1
            return obj

        return InjectApplication(mapp)(fun)

    def test_yielding(self, data, examplefun):
        assert data["name"] == 0
        assert examplefun() == sentinel.name
        assert data["name"] == 1


class TestYieldInjector(Fixtures):
    @fixture
    def exampleinjector(self, data):
        @Injector
        def fun(context, key):
            data[key] = 1
            yield context[key]
            data[key] = 2

        return fun

    @fixture
    def examplefun(self, exampleinjector, mapp, data):
        def fun(obj=exampleinjector("name")):
            assert data["name"] == 1
            return obj

        return InjectApplication(mapp)(fun)

    def test_yielding(self, data, examplefun):
        assert data["name"] == 0
        assert examplefun() == sentinel.name
        assert data["name"] == 2


class TestContextManagerInjector(Fixtures):
    @fixture
    def exampleinjector(self, data):
        class cls(ContextManagerInjector):
            def __enter__(self, context, key):
                data[key] = 1
                return context[key]

            def __exit__(self, exc_type, exc_value, traceback, context, key):
                data[key] = 2

        return cls

    @fixture
    def examplefun(self, exampleinjector, mapp, data):
        def fun(obj=exampleinjector("name")):
            assert data["name"] == 1
            return obj

        return InjectApplication(mapp)(fun)

    def test_context_manager(self, data, examplefun):
        assert data["name"] == 0
        assert examplefun() == sentinel.name
        assert data["name"] == 2
