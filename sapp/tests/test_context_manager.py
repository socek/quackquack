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
        context.example2 = sentinel.example2


class ExampleConfigurator(Configurator):
    def append_plugins(self):
        super().append_plugins()
        self.plugin1 = MagicMock()
        self.plugin2 = MagicMock()
        self.plugin3 = ExamplePlugin()

        self.add_plugin(self.plugin1)
        self.add_plugin(self.plugin2)
        self.add_plugin(self.plugin3)


class TestContextManager(object):
    @fixture
    def configurator(self):
        return ExampleConfigurator()

    def test_when_not_started(self, configurator):
        """
        Configurator should raise an error when it will be used without starting
        it in the first place.
        """
        with raises(ConfiguratorNotStartedError):
            with ContextManager(configurator):
                pass

    def test_many_times(self, configurator):
        """
        Using configurator as context manager should enter and exit plugins only
        once.
        """
        configurator.start()

        with ContextManager(configurator) as app:
            with ContextManager(configurator) as app:
                configurator.plugin1.enter.assert_called_once_with(app)
                configurator.plugin2.enter.assert_called_once_with(app)

        configurator.plugin1.exit.assert_called_once_with(app, None, None, None)
        configurator.plugin2.exit.assert_called_once_with(app, None, None, None)

    def test_when_error_raised(self, configurator):
        """
        When using configurator as context manager and an exception is raised,
        all plugins should get that exception.
        """
        configurator.start()
        error = RuntimeError()

        with raises(RuntimeError):
            with ContextManager(configurator) as app:
                raise error

        configurator.plugin1.start.assert_called_once_with(configurator)
        configurator.plugin2.start.assert_called_once_with(configurator)

        call = configurator.plugin1.exit.call_args_list[0][0]
        assert call[0] == app
        assert call[1] == RuntimeError
        assert call[2] == error
        assert call[3] is not None

        call = configurator.plugin2.exit.call_args_list[0][0]
        assert call[0] == app
        assert call[1] == RuntimeError
        assert call[2] == error
        assert call[3] is not None

    def test_when_using_argument(self, configurator):
        """
        When using configurator as context manager with argument, it will pass
        proper object to the with statement,
        """
        configurator.start()

        with ContextManager(configurator, "example") as example:
            assert example == sentinel.example

    def test_when_using_argument_as_list(self, configurator):
        """
        When using configurator as context manager with argument as list, it
        will pass proper objects to the with statement,
        """
        configurator.start()

        with ContextManager(configurator, ["example"]) as [example]:
            assert example == sentinel.example

    def test_when_wrong_argument_type(self, configurator):
        """
        When using configurator as context manager with wrong argument, it will
        raise AttributeError.
        """
        configurator.start()

        with raises(AttributeError):
            with ContextManager(configurator, 1):
                pass
