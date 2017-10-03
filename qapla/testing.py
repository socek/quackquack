from mock import MagicMock
from mock import patch
from pytest import fixture
from pytest import mark


@mark.integration
class BaseApplicationFixture(object):
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


class ControllerFixtureMixin(object):
    """
    In able to use this mixin, your test class needs to have fixture named "ctrl".
    @fixture
    def ctrl(self, mroot_factory, mrequest):
        return Controller(mroot_factory, mrequest)
    """

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def mroot_factory(self):
        return MagicMock()

    @fixture
    def mrequest(self, app):
        obj = MagicMock()
        obj.registry = dict(application=app)
        return obj

    @fixture
    def mcreate_context(self, ctrl):
        with patch.object(ctrl, '_create_context') as mock:
            yield mock

    @fixture
    def mbefore_make(self, ctrl):
        with patch.object(ctrl, '_before_make') as mock:
            yield mock

    @fixture
    def m_make(self, ctrl):
        with patch.object(ctrl, '_make') as mock:
            yield mock

    @fixture
    def mmake(self, ctrl):
        with patch.object(ctrl, 'make') as mock:
            yield mock

    @fixture
    def mafter_make(self, ctrl):
        with patch.object(ctrl, '_after_make') as mock:
            yield mock

    @fixture
    def mget_response(self, ctrl):
        with patch.object(ctrl, '_get_response') as mock:
            yield mock

    @fixture
    def mbefore_quit(self, ctrl):
        with patch.object(ctrl, '_before_quit') as mock:
            yield mock

    @fixture
    def mcreate_widgets(self, ctrl):
        with patch.object(ctrl, '_create_widgets') as mock:
            yield mock


class FormControllerFixtureMixin(ControllerFixtureMixin):

    @fixture
    def mprepare_context(self, ctrl):
        with patch.object(ctrl, 'prepare_context') as mock:
            yield mock

    @fixture
    def mschema_validated(self, ctrl):
        with patch.object(ctrl, 'schema_validated') as mock:
            yield mock

    @fixture
    def mset_form_error(self, ctrl):
        with patch.object(ctrl, 'set_form_error') as mock:
            yield mock
