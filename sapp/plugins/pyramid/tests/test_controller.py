from unittest.mock import patch
from unittest.mock import sentinel

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pytest import fixture
from pytest import mark
from pytest import raises

from sapp.plugins.pyramid.controller import Controller
from sapp.plugins.pyramid.controller import FinalizeController
from sapp.plugins.pyramid.controller import JsonController
from sapp.plugins.pyramid.controller import QuitController
from sapp.plugins.pyramid.controller import RestfulController
from sapp.plugins.pyramid.testing import ControllerFixtureMixin


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
        return Controller(mroot_factory, mrequest)

    def test_normal_run(
            self,
            ctrl,
            mcreate_context,
            mbefore_make,
            m_make,
            mafter_make,
            mget_response,
            mbefore_quit,
    ):
        """
        In the normal situation, controller should:
        - create context
        - run before make method
        - run make method
        - run after make method
        - return response (from data from .context)
        """
        assert ctrl() == mget_response.return_value

        mcreate_context.assert_called_once_with()
        mbefore_make.assert_called_once_with()
        m_make.assert_called_once_with()
        mafter_make.assert_called_once_with()
        mget_response.assert_called_once_with(m_make.return_value)

        assert not mbefore_quit.called

    def test_on_quit(
            self,
            ctrl,
            mcreate_context,
            mbefore_make,
            m_make,
            mafter_make,
            mget_response,
            mbefore_quit,
    ):
        """
        When .make will raise QuitController, controller should:
        - create context
        - run before make method
        - run make method
        - run after make method
        - do not run after make method
        - return ctrl.response )
        """
        ctrl.response = sentinel.response
        m_make.side_effect = QuitController()

        assert ctrl() == sentinel.response

        mcreate_context.assert_called_once_with()
        mbefore_make.assert_called_once_with()
        m_make.assert_called_once_with()
        assert not mafter_make.called
        assert not mget_response.called
        mbefore_quit.assert_called_once_with()

    def test_on_quit_with_response(
            self,
            ctrl,
            mcreate_context,
            mbefore_make,
            m_make,
            mafter_make,
            mget_response,
            mbefore_quit,
    ):
        """
        When .make will raise QuitController(response), controller should:
        - create context
        - run before make method
        - run make method
        - run after make method
        - do not run after make method
        - return error.response )
        """
        m_make.side_effect = QuitController(sentinel.response)

        assert ctrl() == sentinel.response

        mcreate_context.assert_called_once_with()
        mbefore_make.assert_called_once_with()
        m_make.assert_called_once_with()
        assert not mafter_make.called
        assert not mget_response.called
        mbefore_quit.assert_called_once_with()

    def test_make(self, ctrl, mmake):
        """
        ._make should run .make.
        This method is only container for try/catch.
        """
        ctrl._make()

        mmake.assert_called_once_with()

    def test_make_on_finalize(self, ctrl, mmake):
        """
        ._make should append ctrl.context with FinalizeController's one.
        """
        mmake.side_effect = FinalizeController({'hi': 'you'})
        ctrl.context = {'you': 'too'}

        ctrl._make()

        assert ctrl.context == {'hi': 'you', 'you': 'too'}
        mmake.assert_called_once_with()

    @mark.parametrize('method', [
        '_before_make', '_after_make', '_create_widgets', '_before_quit',
        'make'
    ])
    def test_sanity(self, ctrl, method):
        """
        This test is sanity check if non of the "ready to be overwritten" method has syntax error.
        """
        assert getattr(ctrl, method)() is None

    def test_create_context(self, ctrl, mrequest):
        """
        ._create_context should create default context with request object in it, so it can be used in the templates.
        """
        ctrl._create_context()

        assert ctrl.context == {'request': mrequest}

    def test_get_response(self, ctrl, mcreate_widgets):
        """
        ._get_response should create widgets and return context when no response object was created
        """
        ctrl.context = sentinel.context

        assert ctrl._get_response() == sentinel.context
        mcreate_widgets.assert_called_once_with()

    def test_get_response_when_response_returned_from_make(self, ctrl, mcreate_widgets):
        """
        ._get_response should return response from object returned by .make
        """
        ctrl.context = sentinel.context
        result = sentinel.result

        assert ctrl._get_response(result) == sentinel.result
        assert not mcreate_widgets.called

    def test_get_response_when_response_ready(self, ctrl):
        """
        ._get_response should return response object when one was created
        """
        ctrl.response = sentinel.response

        assert ctrl._get_response() == sentinel.response

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


class TestJsonController(FixturesMixin):
    @fixture
    def ctrl(self, mroot_factory, mrequest):
        return JsonController(mroot_factory, mrequest)

    def test_create_context(self, ctrl):
        """
        JsonController returns everything from context into response, that is why the context should be empty at
        startup.
        """
        ctrl._create_context()

        assert ctrl.context == {}


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
