from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.request import Request
from pyramid.traversal import DefaultRootFactory


class View:
    def __init__(self, root_factory: DefaultRootFactory, request: Request):
        self.request = request
        self.root_factory = root_factory

    @property
    def methods(self):
        return {
            "GET": self.get,
            "POST": self.post,
            "PUT": self.put,
            "PATCH": self.patch,
            "DELETE": self.delete,
            "OPTIONS": self.options,
        }

    def __call__(self):
        method = self.methods[self.request.method]
        return method(self.request)

    def get(self, request: Request):
        raise HTTPMethodNotAllowed()

    def post(self, request: Request):
        raise HTTPMethodNotAllowed()

    def put(self, request: Request):
        raise HTTPMethodNotAllowed()

    def patch(self, request: Request):
        raise HTTPMethodNotAllowed()

    def delete(self, request: Request):
        raise HTTPMethodNotAllowed()

    def options(self, request: Request):
        raise HTTPMethodNotAllowed()


class RestfulView(View):
    """
    View which will return context as json.
    """

    renderer = "json"
