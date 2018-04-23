from unittest.mock import sentinel

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pytest import fixture
from pytest import mark
from pytest import raises

from sapp.plugins.pyramid.views import View
from sapp.plugins.pyramid.views import RestfulView
from sapp.plugins.pyramid.testing import ViewFixtureMixin


class ExampleView(View):
    def get(self):
        return sentinel.response


class TestRestfulView(ViewFixtureMixin):
    @fixture
    def view(self, mroot_factory, mrequest):
        return RestfulView(mroot_factory, mrequest)

    @mark.parametrize('method',
                      ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    def test_methods(self, view, method, mrequest):
        """
        RestfulView has additional methods for every HTTP method used in the REST. This test is validating if
        every method which was not overwritten, will raise HTTPMethodNotAllowed
        """
        mrequest.method = method

        with raises(HTTPMethodNotAllowed):
            view()
