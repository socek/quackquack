from colander import Invalid
from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
from pytest import raises

from qapla.controller import Controller
from qapla.controller import FinalizeController
from qapla.controller import FormController
from qapla.controller import JsonController
from qapla.controller import QuitController
from qapla.controller import RestfulController
from qapla.testing import ControllerFixtureMixin


class FixturesMixin(ControllerFixtureMixin):

    @fixture
    def mhttp_found(self):
        with patch('qapla.controller.HTTPFound') as mock:
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
        mget_response.assert_called_once_with()

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

    @mark.parametrize(
        'method',
        ['_before_make', '_after_make', '_create_widgets', '_before_quit', 'make'])
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

    def test_settings(self, ctrl, mrequest):
        """
        .settings should be a settings object from registry.
        """
        mrequest.registry = dict(settings=sentinel.settings)
        assert ctrl.settings == sentinel.settings


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

    @mark.parametrize(
        'method',
        ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def test_methods(self, ctrl, method, mrequest):
        """
        RestfulController has additional methods for every HTTP method used in the REST. This test is validating if
        every method is covered.
        """
        mrequest.method = method

        ctrl.make()  # syntax check

        with patch.object(ctrl, method.lower()) as mock:
            ctrl.make()
            mock.assert_called_once_with()


class TestFormController(FixturesMixin):

    @fixture
    def ctrl(self, mroot_factory, mrequest):
        return FormController(mroot_factory, mrequest)

    @fixture
    def json(self, mrequest):
        mrequest.json_body = {}
        return mrequest.json_body

    @fixture
    def context(self, ctrl):
        ctrl.context = {}
        return ctrl.context

    @fixture
    def mparse_errors(self, ctrl):
        with patch.object(ctrl, 'parse_errors') as mock:
            yield mock

    @fixture
    def mset_http_error(self, ctrl):
        with patch.object(ctrl, 'set_http_error') as mock:
            yield mock

    def test_prepare_context(self, ctrl, json, context):
        """
        .prepare_context should get values from HTTP's json_body and move it to the context
        """
        json['name1'] = 'value1'

        fields = ctrl.prepare_context()

        assert fields == {
            'name1': 'value1',
        }
        assert ctrl.context['errors'] == []

    def test_schema_validated(self, ctrl):
        """
        .schema_validated should use colander way to validate data. Status of the validation should be returned.
        """
        schema = MagicMock()
        fields = MagicMock()
        ctrl.context = {}

        assert ctrl.schema_validated(schema, fields)
        schema.deserialize.assert_called_once_with(fields)

    def test_schema_validated_when_failed(self, ctrl, mrequest, mparse_errors):
        """
        .schema_validated should use colander way to validate data. When colander raise and error, the method should
        parse error, change response to HTTP 403 and return False.
        """
        schema = MagicMock()
        error = Invalid(MagicMock())
        schema.deserialize.side_effect = error
        fields = MagicMock()
        ctrl.context = {}

        assert not ctrl.schema_validated(schema, fields)
        mparse_errors.assert_called_once_with(fields, error)
        assert mrequest.response.status_code == 403

    def test_parse_errors(self, ctrl):
        """
        .parse_errors should parse errors from colander, which are in form {input_name: error_message}, to rotarran
        form data schema.
        """
        ctrl.context = dict(errors=[])
        error = MagicMock()
        error.asdict.return_value = {'name1': 'error1'}

        fields = {
            'name1': 'value1',
            'name2': 'value2',
        }

        ctrl.parse_errors(fields, error)

        assert ctrl.context['errors'] == [{'type': 'field', 'message': 'error1', 'field': 'name1'}]

    def test_set_form_error(self, ctrl, mset_http_error):
        """
        .set_form_error should set response error and add proper error object in the context.
        """
        ctrl.context = dict(errors=[])

        ctrl.set_form_error(sentinel.error_message)

        mset_http_error.assert_called_once_with()
        assert ctrl.context == {
            'errors': [{'type': 'form', 'message': sentinel.error_message}]
        }
