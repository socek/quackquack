from unittest.mock import MagicMock

from pytest import fixture

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
