from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from qq.application import AlreadyStartedError
from qq.application import Application
from qq.plugin import Plugin


class ExamplePlugin(Plugin):
    def enter(self, context):
        context["example"] = sentinel.example


class ExampleApplication(Application):
    def create_plugins(self):
        super().create_plugins()
        self.plugins["plugin1"] = MagicMock(key=None)
        self.plugins["plugin2"] = MagicMock(key=None)
        self.plugins["plugin3"] = ExamplePlugin()


class TestApplication:
    @fixture
    def app(self):
        return ExampleApplication()

    def test_start(self, app):
        """
        .start should append plugins and init them. Also proper flags should be
        set.
        """
        app.start("wsgi", wsgi=1)

        plugin1 = app.plugins["plugin1"]
        plugin2 = app.plugins["plugin2"]

        assert app.extra == {"wsgi": 1}
        assert app.globals == {
            "plugin1": plugin1.start.return_value,
            "plugin2": plugin2.start.return_value,
            "plugin3": None,
        }
        assert app.startpoint == "wsgi"
        assert app.is_started

        plugin1.start.assert_called_once_with(app)
        plugin2.start.assert_called_once_with(app)

    def test_start_when_started(self, app):
        """
        .start should do nothing if app already started
        """
        app.is_started = True

        with raises(AlreadyStartedError):
            assert app.start("wsgi", wsgi=1)

        assert app.globals == {}
        assert app.startpoint is None
        assert app.plugins == {}
