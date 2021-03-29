from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.injector import ContextManagerInjector
from qq.injector import InjectApplicationContext
from qq.injector import Injector


class Fixtures:
    @fixture
    def data(self):
        return {
            "name": 0,
        }

    @fixture
    def app(self):
        app = MagicMock()
        app.context.get.return_value = {
            "name": sentinel.name,
        }
        return app


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
    def examplefun(self, exampleinjector, app, data):
        def fun(obj=exampleinjector(app, "name")):
            assert data["name"] == 1
            return obj

        return InjectApplicationContext(fun)

    def test_yielding(self, data, examplefun):
        assert data["name"] == 0
        assert examplefun() == sentinel.name
        assert data["name"] == 2


class TestContextManagerInjector(Fixtures):
    @fixture
    def exampleinjector(self, data):
        class cls(ContextManagerInjector):
            def enter(self, context, key):
                data[key] = 1
                return context[key]

            def exit(self, exc_type, exc_value, traceback, context, key):
                data[key] = 2

        return cls

    @fixture
    def examplefun(self, exampleinjector, app, data):
        def fun(obj=exampleinjector(app, "name")):
            assert data["name"] == 1
            return obj

        return InjectApplicationContext(fun)

    def test_context_manager(self, data, examplefun):
        assert data["name"] == 0
        assert examplefun() == sentinel.name
        assert data["name"] == 2
