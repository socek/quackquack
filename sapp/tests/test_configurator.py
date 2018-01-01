from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture
from pytest import raises

from sapp.configurator import Configurator
from sapp.configurator import ConfiguratorNotStartedError


class ExampleConfigurator(Configurator):
    def append_plugins(self):
        super().append_plugins()
        self.plugin1 = MagicMock()
        self.plugin2 = MagicMock()

        self.add_plugin(self.plugin1)
        self.add_plugin(self.plugin2)


class TestConfigurator(object):
    @fixture
    def configurator(self):
        return ExampleConfigurator()

    def test_configurator_on_not_started(self, configurator):
        """
        Configurator should raise an error when it will be used without starting
        it in the first place.
        """
        with raises(ConfiguratorNotStartedError):
            with configurator:
                pass

    def test_start(self, configurator):
        """
        .start should append plugins and init them. Also proper flags should be
        set.
        """
        configurator.start('wsgi', wsgi=1)

        assert configurator.extra == {'wsgi': 1}
        assert configurator.startpoint == 'wsgi'
        assert configurator.is_started

        configurator.plugin1.start.assert_called_once_with(configurator)
        configurator.plugin2.start.assert_called_once_with(configurator)

        assert configurator.plugins == [
            configurator.plugin1, configurator.plugin2
        ]

    def test_context_manager_many_times(self, configurator):
        """
        Using configurator as context manager should enter and exit plugins only
        once.
        """
        configurator.start()

        with configurator as app:
            with configurator as app:
                configurator.plugin1.enter.assert_called_once_with(app)
                configurator.plugin2.enter.assert_called_once_with(app)

        configurator.plugin1.start.assert_called_once_with(configurator)
        configurator.plugin2.start.assert_called_once_with(configurator)

        configurator.plugin1.exit.assert_called_once_with(
            app, None, None, None)
        configurator.plugin2.exit.assert_called_once_with(
            app, None, None, None)

    def test_context_manager_when_raised(self, configurator):
        """
        When using configurator as context manager and an exception is raised,
        all plugins should get that exception.
        """
        configurator.start()
        error = RuntimeError()

        with raises(RuntimeError):
            with configurator as app:
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

    def test_mocking(self, configurator):
        """
        Mocking the application objects should be simple an easy.
        """
        with patch.object(configurator, 'create_context') as mock:
            with configurator as app:
                assert app == mock.return_value
