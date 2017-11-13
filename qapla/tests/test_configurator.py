from mock import patch
from pytest import fixture
from pytest import raises

from qapla.configurator import Configurator
from qapla.plugin import Plugin


class SamplePlugin(Plugin):
    def __init__(self):
        self.cool = 0

    def init_pyramid(self, pyramid):
        super().init_pyramid(pyramid)
        pyramid.hi_pyramid = True

    def enter(self, application):
        super().enter(application)
        self.cool += 1
        application.cool = self.cool

    def exit(self, application, exc_type, exc_value, traceback):
        super().exit(application, exc_type, exc_value, traceback)
        self.cool -= 1


class SampleConfigurator(Configurator):
    def append_plugins(self):
        super().append_plugins()
        self.add_plugin(SamplePlugin())


class TestNewApplication(object):
    @fixture
    def mpyramid(self):
        with patch('qapla.configurator.PyramidConfigurator') as mock:
            yield mock

    def test_simple_app(self):
        configurator = SampleConfigurator()
        configurator.start_configurator('command')

        with configurator as app:
            assert app.cool == 1

    def test_double_app(self):
        configurator = SampleConfigurator()
        configurator.start_configurator('command')

        with configurator as app1:
            with configurator as app2:
                assert app1.cool == 1
                assert app2.cool == 1

    def test_not_started(self):
        configurator = SampleConfigurator()

        with raises(RuntimeError):
            with configurator:
                pass

    def test_uwsgi(self, mpyramid):
        mapp = mpyramid.return_value

        configurator = SampleConfigurator()

        assert configurator() == mapp.make_wsgi_app.return_value
        assert mapp.hi_pyramid is True
        mpyramid.assert_called_once_with()
        mapp.make_wsgi_app.assert_called_once_with()

