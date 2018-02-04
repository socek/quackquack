from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPMethodNotAllowed


class QuitController(Exception):
    """
    Immediately ends controller. Controller will return provided response.
    """

    def __init__(self, response=None):
        super().__init__()
        self.response = response


class Controller(object):

    # ********
    # * flow *
    # ********

    def __init__(self, root_factory, request):
        self.request = request
        self.root_factory = root_factory
        self.response = None

    def __call__(self):
        try:
            return self._get_response(self.make())
        except QuitController as end:
            return end.response or self.response

    def _get_response(self, result):
        if result:
            return result
        if self.response:
            return self.response

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


class HttpMixin(object):
    @property
    def methods(self):
        return {
            'GET': self.get,
            'POST': self.post,
            'PUT': self.put,
            'PATCH': self.patch,
            'DELETE': self.delete,
            'OPTIONS': self.options,
        }

    def make(self):
        method = self.methods[self.request.method]
        return method()

    def get(self):
        raise HTTPMethodNotAllowed()

    def post(self):
        raise HTTPMethodNotAllowed()

    def put(self):
        raise HTTPMethodNotAllowed()

    def patch(self):
        raise HTTPMethodNotAllowed()

    def delete(self):
        raise HTTPMethodNotAllowed()

    def options(self):
        raise HTTPMethodNotAllowed()


class HttpController(HttpMixin, Controller):
    pass


class RestfulController(HttpMixin, JsonController):
    pass
