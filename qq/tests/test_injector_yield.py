from contextvars import ContextVar
from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.context import Context


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
