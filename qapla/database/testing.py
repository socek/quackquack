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
        - dbplugin - qapla.database.database.Database instance for the database set by the DATABASE_KEY
        - dbsession - sqlalchemy session for the database set by the DATABASE_KEY. It will be automatically closed
        - settings - settings for the application
        - paths - paths for the application
    """
    SESSION_CACHE = {}
    CONFIGURATOR_CLASS = None

    @fixture(scope="module")
    def config(self):
        """
        This fixture will create full configurator object. It can be use for
        accessing app during the tests.
        """
        key = 'config'
        if key not in self.SESSION_CACHE:
            config = self.CONFIGURATOR_CLASS()
            config.start_configurator('test')
            self.SESSION_CACHE[key] = config
        return self.SESSION_CACHE[key]

    @fixture
    def app(self, config):
        with config as app:
            yield app
