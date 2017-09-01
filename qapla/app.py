from logging.config import dictConfig

from pyramid.config import Configurator

from qapla.settings import SettingsFactory


class Application(object):

    class Config(object):
        settings_module = None
        settings = SettingsFactory

    def __call__(self, settings=None):
        settings = settings or {}
        return self.run_uwsgi(settings)

    def run_uwsgi(self, settings=None):
        """
        Create application with 'uwsgi' settings and return pyramid's uwsgi application object.
        """
        settings = settings or {}
        self._create_app(settings, 'uwsgi')
        return self.config.make_wsgi_app()

    def run_tests(self, settings=None):
        """
        Create application with 'tests' settings.
        """
        settings = settings or {}
        self._create_app(settings, 'tests')

    def run_shell(self, settings=None):
        """
        Create application with 'shell' settings.
        """
        settings = settings or {}
        self._create_app(settings, 'shell')

    def run_command(self, settings=None):
        """
        Create application with 'command' settings.
        """
        settings = settings or {}
        self._create_app(settings, 'command')

    def _create_app(self, settings={}, endpoint='uwsgi'):
        self._generate_settings(settings, endpoint)
        self._create_config()
        self._generate_registry(self.config.registry)
        self.append_plugins()

    def _generate_settings(
        self,
        settings,
        endpoint,
    ):
        self.settings = settings
        self.paths = {}
        factory = self.Config.settings(
            self.Config.settings_module,
            self.settings,
            self.paths)
        self.settings, self.paths = factory.get_for(endpoint)

    def _create_config(self):
        kwargs = self._get_config_kwargs()
        self.config = Configurator(**kwargs)

    def _get_config_kwargs(self):
        return {
            'settings': self.settings.to_dict(),
        }

    def _generate_registry(self, registry):
        self.registry = registry
        registry['settings'] = self.settings
        registry['paths'] = self.paths
        registry['application'] = self

    # Plugins

    def append_plugins(self):
        """
        This is the place to add your plugins.
        """

    def add_routing(self, routing_cls):
        """
        Add routing to the pyramid app.
        """
        self.routing = routing_cls(self)
        self.routing.make()

    def add_auth(
        self,
        authn_policy_cls=None,
        authz_policy_cls=None,
        root_factory=None,
    ):
        """
        Add authorization to the pyramid app.
        """
        authn_policy = authn_policy_cls(self.settings['secret'])
        authz_policy = authz_policy_cls()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)
        if root_factory:
            self.config.set_root_factory(root_factory)

    def add_session(self, session_factory_cls):
        """
        Add session mechanism to the pyramid app.
        """
        session_factory = session_factory_cls(self.settings['session_secret'])
        self.config.set_session_factory(session_factory)

    def add_csrf_policy(self, policy_cls):
        """
        Add csrf mechanism to the pyramid app.
        """
        self.config.set_csrf_storage_policy(policy_cls())
        self.config.set_default_csrf_options(
            require_csrf=True,
            token=self.settings['csrf_token_key'],
            header=self.settings['csrf_header_key'])

    def add_logging(self):
        """
        Add logging configuration. Needs 'logging' value in settings.
        https://docs.python.org/3.6/library/logging.config.html#logging.config.dictConfig
        """
        dictConfig(self.settings['logging'])
