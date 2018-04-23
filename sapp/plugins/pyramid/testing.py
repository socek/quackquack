from unittest.mock import MagicMock

from pytest import fixture
from webtest import TestApp

from sapp.plugins.sqlalchemy.testing import BaseIntegrationFixture


class ViewFixtureMixin(object):
    """
    In able to use this mixin, your test class needs to have fixture named "view".
    @fixture
    def view(self, mroot_factory, mrequest):
        return View(mroot_factory, mrequest)
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


class BaseWebTestFixture(BaseIntegrationFixture):
    UWSGI_KEY = 'wsgi'

    @fixture(scope='module')
    def wsgi_app(self, config):
        if self.UWSGI_KEY not in self.SESSION_CACHE:
            self.SESSION_CACHE[self.UWSGI_KEY] = config.make_wsgi_object()
        return self.SESSION_CACHE[self.UWSGI_KEY]

    @fixture
    def fake_app(self, wsgi_app):
        return TestApp(wsgi_app)
