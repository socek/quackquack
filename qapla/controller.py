from colander import Invalid
from pyramid.httpexceptions import HTTPFound


class QuitController(Exception):
    """
    Immediately ends controller. Controller will return provided response.
    """

    def __init__(self, response=None):
        self.response = response


class FinalizeController(Exception):
    """
    Ends .make method. Other Controller mechanics will work normally.
    """

    def __init__(self, context=None):
        self.context = context or {}


class Controller(object):

    # **************
    # * Properties *
    # **************

    @property
    def settings(self):
        return self.request.registry['settings']

    # ********
    # * flow *
    # ********

    def __init__(self, root_factory, request):
        self.request = request
        self.application = request.registry['application']
        self.root_factory = root_factory
        self.response = None

    def __call__(self):
        return self.run()

    def run(self):
        try:
            self._create_context()
            self._before_make()
            self._make()
            self._after_make()
            return self._get_response()
        except QuitController as end:
            self._before_quit()
            return end.response or self.response

    def _make(self):
        try:
            self.make()
        except FinalizeController as finalizer:
            self.context.update(finalizer.context)

    def _get_response(self):
        if self.response is None:
            self._create_widgets()
            return self.context
        else:
            return self.response

    # **********************************
    # * Method ready to be overwritten *
    # **********************************

    def _create_context(self):
        self.context = {
            'request': self.request,
        }

    def _before_make(self):
        pass

    def _after_make(self):
        pass

    def _create_widgets(self):
        pass

    def _before_quit(self):
        pass

    def make(self):
        pass

    # ******************
    # * Helper methods *
    # ******************

    def redirect(self, to, quit=False, **kwargs):
        url = self.request.route_url(to, **kwargs)
        self.response = HTTPFound(
            location=url,
            headers=self.request.response.headerlist,
        )
        if quit:
            raise QuitController(self.response)


class JsonController(Controller):
    """
    Controller which will return context as json.
    """
    renderer = 'json'

    def _create_context(self):
        self.context = {}


class RestfulController(JsonController):

    @property
    def methods(self):
        return {
            'GET': self.get,
            'POST': self.post,
            'PUT': self.put,
            'PATCH': self.patch,
            'DELETE': self.delete,
        }

    def make(self):
        method = self.methods[self.request.method]
        method()

    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass

    def patch(self):
        pass

    def delete(self):
        pass


class FormController(RestfulController):

    def prepare_context(self):
        """
        Prepere context for returning form data.
        """
        self.context['errors'] = []
        return self.request.json_body

    def schema_validated(self, schema, fields):
        """
        Validate if data provided are in proper schema.
        """
        try:
            schema.deserialize(fields)
            return True
        except Invalid as error:
            self.parse_errors(fields, error)
            self.set_http_error()
            return False

    def parse_errors(self, fields, error):
        """
        Parse errors provided by colander and return in our own form format.
        """
        errors = error.asdict()
        for key, value in errors.items():
            self.context['errors'].append({
                'type': 'field',
                'message': value,
                'field': key,
            })

    def set_http_error(self):
        """
        Set HTTP 403 error on response.
        """
        self.request.response.status_code = 403

    def set_form_error(self, msg):
        """
        Set form's error in context.
        """
        self.context['errors'].append(dict(
            type='form',
            message=msg))
        self.set_http_error()
