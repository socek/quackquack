from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from sapp.plugins.pyramid.configurator import ConfiguratorWithPyramid


class ExampleConfigurator(ConfiguratorWithPyramid):
    def append_plugins(self):
        super().append_plugins()
        self.plugin1 = MagicMock()
        self.plugin2 = MagicMock()
        del (self.plugin2.start_pyramid)

        self.add_plugin(self.plugin1)
        self.add_plugin(self.plugin2)


class TestConfiguratorWithPyramid(object):
    @fixture
    def configurator(self):
        return ExampleConfigurator()

    @fixture
    def mpyramid_configurator(self):
        with patch('sapp.plugins.pyramid.configurator.PyramidConfigurator'
                   ) as mock:
            yield mock

    def test_starting_pyramid_application(self, configurator,
                                          mpyramid_configurator):
        """
        .start_pyramid should create wsgi application
        """
        configurator.start('pyramid')

        configurator.settings = sentinel.settings
        wsgi = configurator.make_wsgi_object('arg', kw='arg2')

        mpyramid_configurator.assert_called_once_with(
            'arg', settings=sentinel.settings, kw='arg2')
        pyramid = mpyramid_configurator.return_value
        pyramid.make_wsgi_app.assert_called_once_with()
        assert pyramid.make_wsgi_app.return_value == wsgi

        configurator.plugin1.start_pyramid.assert_called_once_with(pyramid)
