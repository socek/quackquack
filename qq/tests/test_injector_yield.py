from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq import Injector
from qq.injector import InjectApplicationContext


class TestYieldInjector:
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

    @fixture
    def exampleinjector(self, data):
        def fun(context, key):
            data[key] = 1
            yield context[key]
            data[key] = 2

        return Injector(fun)

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
