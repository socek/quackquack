from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture

from qapla.app import Application


class TestApplication(object):

    @fixture
    def app(self):
        return Application()

    @fixture
    def mconfig(self, app):
        with patch.object(app, 'Config') as mock:
            yield mock

    @fixture
    def mconfigurator(self):
        with patch('qapla.app.Configurator') as mock:
            yield mock

    @fixture
    def mgenerate_settings(self, app):
        with patch.object(app, '_generate_settings') as mock:
            yield mock

    @fixture
    def mcreate_config(self, app):
        with patch.object(app, '_create_config') as mock:
            yield mock

    @fixture
    def mgenerate_registry(self, app):
        with patch.object(app, '_generate_registry') as mock:
            yield mock

    @fixture
    def mcreate_routing(self, app):
        with patch.object(app, '_create_routing') as mock:
            yield mock

    @fixture
    def mcreate_app(self, app):
        with patch.object(app, '_create_app') as mock:
            yield mock

    @fixture
    def mconfig_settings(self, app):
        with patch.object(app.Config, 'settings') as mock:
            yield mock

    @fixture
    def mconfig_settings_mopdule(self, app):
        with patch.object(app.Config, 'settings_module') as mock:
            yield mock

    def test_create_routing(self, app, mconfig):
        """
        .create_routing should get routing class from the Config class and initalize the routing
        """
        app._create_routing()

        mconfig.routing_cls.assert_called_once_with(app)
        mconfig.routing_cls.return_value.make.assert_called_once_with()

    def test_generate_registry(self, app):
        """
        ._generate_registry should add settings, paths and application to the registry.
        Pyramid will pass it on to the request.registry object.
        """
        myregistry = {}

        app.settings = sentinel.settings
        app.paths = sentinel.paths
        app._generate_registry(myregistry)

        assert myregistry == dict(
            settings=sentinel.settings,
            paths=sentinel.paths,
            application=app)

        assert app.registry == myregistry

    def test_create_config(self, app, mconfigurator):
        """
        ._create_config should return pyramid's Config object with configured settings.
        """
        app.settings = MagicMock()

        app._create_config()

        mconfigurator.assert_called_once_with(
            settings=app.settings.to_dict.return_value)
        assert app.config == mconfigurator.return_value
        app.settings.to_dict.assert_called_once_with()

    def test_generate_settings(self, app, mconfig_settings, mconfig_settings_mopdule):
        """
        ._generate_settings should generate settings from factory, which is set in the Application.Config class. This
        method should result in creating app.settings and app.paths.
        """
        app.settings = sentinel.settings
        factory = app.Config.settings.return_value
        factory.get_for.return_value = [sentinel.left, sentinel.right]

        app._generate_settings(sentinel.base_settings, sentinel.endpoint)

        app.Config.settings.assert_called_once_with(
            mconfig_settings_mopdule,
            sentinel.base_settings,
            {})
        factory.get_for.assert_called_once_with(sentinel.endpoint)

        assert app.settings == sentinel.left
        assert app.paths == sentinel.right

    def test_create_app(
        self,
        app,
        mgenerate_settings,
        mcreate_config,
        mgenerate_registry,
        mcreate_routing,
    ):
        """
        ._create_app should create Application for provided endpoint
        """
        settings = sentinel.settings
        endpoint = sentinel.endpoint
        app.config = MagicMock()

        app._create_app(settings, endpoint)

        mgenerate_settings.assert_called_once_with(settings, endpoint)
        mcreate_config.assert_called_once_with()
        mgenerate_registry.assert_called_once_with(app.config.registry)
        mcreate_routing.assert_called_once_with()

    def test_run_command(self, app, mcreate_app):
        """
        .run_command should create app for 'command' endpoint
        """
        app.run_command()

        mcreate_app.assert_called_once_with({}, 'command')

    def test_run_shell(self, app, mcreate_app):
        """
        .run_shell should create app for 'shell' endpoint
        """
        app.run_shell()

        mcreate_app.assert_called_once_with({}, 'shell')

    def test_run_tests(self, app, mcreate_app):
        """
        .run_tests should create app for 'tests' endpoint
        """
        app.run_tests()

        mcreate_app.assert_called_once_with({}, 'tests')

    def test_run_uwsgi(self, app, mcreate_app):
        """
        .run_uwsgi should create app for 'uwsgi' endpoint and return uwsgi application.
        """
        app.config = MagicMock()

        assert app.run_uwsgi() == app.config.make_wsgi_app.return_value

        mcreate_app.assert_called_once_with({}, 'uwsgi')
        app.config.make_wsgi_app.assert_called_once_with()

    def test_call(self, app, mcreate_app):
        """
        .__call__ should create app for 'uwsgi' endpoint and return uwsgi application.
        """
        app.config = MagicMock()

        assert app() == app.config.make_wsgi_app.return_value

        mcreate_app.assert_called_once_with({}, 'uwsgi')
        app.config.make_wsgi_app.assert_called_once_with()
