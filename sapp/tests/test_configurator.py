from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from sapp.configurator import Configurator
from sapp.configurator import ConfiguratorNotStartedError
from sapp.context_manager import ContextManager
from sapp.plugin import Plugin


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


class TestConfigurator(object):
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
