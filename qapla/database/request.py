class RequestDBSessionGenerator(object):

    def __init__(self, registry_key):
        self.registry_key = registry_key

    def __call__(self, request):
        request_db = RequestDBSession(request, self.registry_key)
        request.add_finished_callback(request_db.cleanup)
        return request_db.run()


class RequestDBSession(object):

    def __init__(self, request, registry_key):
        self.request = request
        self.registry_key = registry_key

    def run(self):
        self._create_maker()
        self._create_session()
        return self.session

    def _create_maker(self):
        self.maker = self.request.registry[self.registry_key]

    def _create_session(self):
        self.session = self.maker()

    def cleanup(self, request):
        if request.exception is not None:
            self.session.rollback()
        self.maker.remove()
