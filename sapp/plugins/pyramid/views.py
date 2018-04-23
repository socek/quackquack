from pyramid.httpexceptions import HTTPMethodNotAllowed


class View(object):
    def __init__(self, root_factory, request):
        self.request = request
        self.root_factory = root_factory

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

    def __call__(self):
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


class RestfulView(View):
    """
    View which will return context as json.
    """
    renderer = 'json'
