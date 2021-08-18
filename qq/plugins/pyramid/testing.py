from unittest.mock import MagicMock

from pytest import fixture


class ViewFixture:
    """
    In able to use this mixin, your test class needs to have fixture named "view".
    @fixture
    def view(self, mroot_factory, mrequest):
        return View(mroot_factory, mrequest)
    """

    _view = None

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def mroot_factory(self):
        return MagicMock()

    @fixture
    def mrequest(self, app):
        request = MagicMock()
        request.registry = dict(application=app)
        request._cache = {}
        request.GET = {}
        request.POST = {}
        request.matchdict = {}
        request.json_body = {}
        request.headers = {}
        return request

    @fixture
    def matchdict(self, mrequest):
        return mrequest.matchdict

    @fixture
    def view(self, mroot_factory, mrequest):
        return self._view(mroot_factory, mrequest)
