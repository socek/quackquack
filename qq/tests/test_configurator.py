from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.configurator import Configurator
from qq.plugin import Plugin


class ExamplePlugin(Plugin):
    def enter(self, context):
        context.example = sentinel.example


class ExampleConfigurator(Configurator):
    def append_plugins(self):
        super().append_plugins()
        self.plugin1 = MagicMock()
        self.plugin2 = MagicMock()
        self.plugin3 = ExamplePlugin()

        self.add_plugin(self.plugin1)
        self.add_plugin(self.plugin2)
        self.add_plugin(self.plugin3)


class TestConfigurator:
    @fixture
    def configurator(self):
        return ExampleConfigurator()

    def test_start(self, configurator):
        """
        .start should append plugins and init them. Also proper flags should be
        set.
        """
        configurator.start("wsgi", wsgi=1)

        assert configurator.extra == {"wsgi": 1}
        assert configurator.startpoint == "wsgi"
        assert configurator.is_started

        configurator.plugin1.start.assert_called_once_with(configurator)
        configurator.plugin2.start.assert_called_once_with(configurator)

        assert configurator.plugins == [
            configurator.plugin1,
            configurator.plugin2,
            configurator.plugin3,
        ]

    def test_start_when_started(self, configurator):
        """
        .start should do nothing if configurator already started
        """
        configurator.is_started = True

        assert configurator.start("wsgi", wsgi=1) is False

        assert configurator.extra == {}
        assert configurator.startpoint is None
        assert configurator.plugins == []
