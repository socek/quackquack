from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from qq.plugins.pyramid.configurator import PyramidApplication
from qq.plugins.settings import SettingsPlugin

PREFIX = "qq.plugins.pyramid.configurator"


class ExampleApplication(PyramidApplication):
    def create_plugins(self):
        super().create_plugins()
        self.plugins["plugin1"] = MagicMock()
        self.plugins["plugin2"] = MagicMock()
        del self.plugins["plugin2"].start_pyramid


class TestPyramidApplication:
    @fixture
    def configurator(self):
        return ExampleApplication()

    @fixture
    def mpyramid_configurator(self):
        with patch(f"{PREFIX}.Configurator") as mock:
            yield mock

    def test_starting_pyramid_application(
        self, configurator, mpyramid_configurator
    ):
        """
        .start_pyramid should create wsgi application
        """
        configurator.start("pyramid")

        configurator.globals[SettingsPlugin.DEFAULT_KEY] = sentinel.settings
        wsgi = configurator.make_wsgi_object("arg", kw="arg2")

        mpyramid_configurator.assert_called_once_with(
            "arg", settings=sentinel.settings, kw="arg2"
        )
        pyramid = mpyramid_configurator.return_value
        pyramid.make_wsgi_app.assert_called_once_with()
        assert pyramid.make_wsgi_app.return_value == wsgi

        configurator.plugins["plugin1"].start_pyramid.assert_called_once_with(
            pyramid
        )