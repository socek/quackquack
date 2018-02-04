from unittest.mock import patch
from unittest.mock import sentinel

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pytest import fixture
from pytest import mark
from pytest import raises

from sapp.plugins.pyramid.controller import Controller
from sapp.plugins.pyramid.controller import QuitController
from sapp.plugins.pyramid.controller import RestfulController
from sapp.plugins.pyramid.testing import ControllerFixtureMixin


class ExampleController(Controller):
    def make(self):
        return sentinel.response


class FixturesMixin(ControllerFixtureMixin):
    @fixture
    def mhttp_found(self):
        with patch('sapp.plugins.pyramid.controller.HTTPFound') as mock:
            yield mock


class TestController(FixturesMixin):
    """
    This test is for validation flow of the controller object.
    """

    @fixture
    def ctrl(self, mroot_factory, mrequest):
        return ExampleController(mroot_factory, mrequest)

    @fixture
    def mmake(self, ctrl):
        with patch.object(ctrl, 'make') as mock:
            yield mock

    def test_normal_run(
            self,
            ctrl,
    ):
        """
        In the normal situation, controller should return response created by
        .make method.
        """
        assert ctrl() == sentinel.response

    def test_on_quit(
            self,
            ctrl,
            mmake,
    ):
        """
        When .make will raise QuitController, controller should return
        ctrl.response
        """
        ctrl.response = sentinel.response
        mmake.side_effect = QuitController()

        assert ctrl() == sentinel.response

    def test_on_quit_with_response(
            self,
            ctrl,
            mmake,
    ):
        """
        When .make will raise QuitController with response argument, controller
        should return response from the exception
        """
        ctrl.response = sentinel.response
        mmake.side_effect = QuitController(sentinel.raised_response)

        assert ctrl() == sentinel.raised_response

    def test_get_response(self, ctrl):
        """
        ._get_response should create widgets and return context when no response object was created
        """
        assert ctrl._get_response(None) is None

    def test_get_response_when_response_returned_from_make(self, ctrl):
        """
        ._get_response should return response from object returned by .make
        """
        assert ctrl._get_response(sentinel.result) == sentinel.result

    def test_get_response_when_response_ready(self, ctrl):
        """
        ._get_response should return response object when one was created
        """
        ctrl.response = sentinel.response

        assert ctrl._get_response(None) == sentinel.response

    def test_redirect(self, ctrl, mrequest, mhttp_found):
        """
        .redirect should create redirection response.
        """
        ctrl.redirect('homeland', additional=True)

        mrequest.route_url.assert_called_once_with('homeland', additional=True)
        mhttp_found.assert_called_once_with(
            location=mrequest.route_url.return_value,
            headers=mrequest.response.headerlist)

    def test_redirect_with_quit(self, ctrl, mrequest, mhttp_found):
        """
        .redirect should create redirection response and raise QuitController with the response
        """
        with raises(QuitController):
            ctrl.redirect('homeland', True)

        mrequest.route_url.assert_called_once_with('homeland')
        mhttp_found.assert_called_once_with(
            location=mrequest.route_url.return_value,
            headers=mrequest.response.headerlist)


class TestRestfulController(FixturesMixin):
    @fixture
    def ctrl(self, mroot_factory, mrequest):
        return RestfulController(mroot_factory, mrequest)

    @mark.parametrize('method',
                      ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    def test_methods(self, ctrl, method, mrequest):
        """
        RestfulController has additional methods for every HTTP method used in the REST. This test is validating if
        every method which was not overwritten, will raise HTTPMethodNotAllowed
        """
        mrequest.method = method

        with raises(HTTPMethodNotAllowed):
            ctrl.make()
