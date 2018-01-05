from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture
from webtest import TestApp

from sapp.plugins.sqlalchemy.testing import BaseIntegrationFixture


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


class BaseWebTestFixture(BaseIntegrationFixture):
    UWSGI_KEY = 'wsgi'

    @fixture(scope='module')
    def wsgi_app(self, config):
        if self.UWSGI_KEY not in self.SESSION_CACHE:
            self.SESSION_CACHE[self.UWSGI_KEY] = config.make_wsgi_app()
        return self.SESSION_CACHE[self.UWSGI_KEY]

    @fixture
    def fake_app(self, wsgi_app):
        return TestApp(wsgi_app)
