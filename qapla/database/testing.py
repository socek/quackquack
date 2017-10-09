from pytest import fixture
from pytest import mark


@mark.integration
class BaseApplicationFixture(object):
    """
    This test class is responsible for starting the application in test mode.
    The tests implemented under this class will get the @mark.integration mark,
    so please use this class only when needed.

    To configure you need to set these 2 class properties:
        - APP_CLASS - class from which create the application. It should be inherited from qapla.database.application.DatabaseApplication
        - DATABASE_KEY - key of the database, default: 'database'

    List of avalible fixtures:
        - application - CCAdsApplication instance with tests settings.
        - dbplugin - qapla.database.database.Database instance for the database set by the DATABASE_KEY
        - dbsession - sqlalchemy session for the database set by the DATABASE_KEY. It will be automatically closed
        - settings - settings for the application
        - paths - paths for the application
    """
    _test_cache = None
    _test_app = None
    APP_CLASS = None
    DATABASE_KEY = 'database'

    @fixture(scope="module")
    def _cache(self):
        if not BaseApplicationFixture._test_cache:
            BaseApplicationFixture._test_cache = {}
        return BaseApplicationFixture._test_cache

    @fixture(scope="module")
    def application(self):
        """
        This fixture will create full application object. It can be use for accessing the db in tests.
        """
        if not BaseApplicationFixture._test_app:
            app = self.APP_CLASS()
            app.run_tests()
            BaseApplicationFixture._test_app = app
        return BaseApplicationFixture._test_app

    @fixture(scope='module')
    def dbplugin(self, application, _cache):
        has_inited = _cache.get('has_inited', False)
        db = application.dbs[self.DATABASE_KEY]
        if not has_inited:
            _cache['has_inited'] = True
            db.recreate()
        return db

    @fixture
    def dbsession(self, dbplugin):
        session = dbplugin.get_session()
        yield session
        session.rollback()
        dbplugin.sessionmaker.remove()

    @fixture
    def settings(self, application):
        return application.settings

    @fixture
    def paths(self, application):
        return application.paths
