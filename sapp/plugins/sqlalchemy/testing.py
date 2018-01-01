from pytest import fixture
from pytest import mark


@mark.integration
class BaseIntegrationFixture(object):
    """
    This test class is responsible for starting the application in test mode.
    The tests implemented under this class will get the @mark.integration mark,
    so please use this class only when needed.

    To configure you need to set these 2 class properties:
        - CONFIGURATOR_CLASS - Sass's Configurator class.

    List of avalible fixtures:
        - config - Sapp's Configurator instance with tests settings.
        - app - Sapp's application instance
    """
    SESSION_CACHE = {}
    CONFIGURATOR_CLASS = None
    CONFIGURATOR_KEY = 'config'

    def after_configurator_start(self, config):
        pass

    @fixture(scope="module")
    def config(self):
        """
        This fixture will create full configurator object. It can be use for
        accessing app during the tests.
        """
        if self.CONFIGURATOR_KEY not in self.SESSION_CACHE:
            config = self.CONFIGURATOR_CLASS()
            config.start('tests')
            self.SESSION_CACHE[self.CONFIGURATOR_KEY] = config
            self.after_configurator_start(config)
        return self.SESSION_CACHE[self.CONFIGURATOR_KEY]

    @fixture
    def app(self, config):
        with config as app:
            yield app
