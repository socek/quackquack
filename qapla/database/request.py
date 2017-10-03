class RequestDBSessionGenerator(object):

    def __init__(self, registry_key):
        self.registry_key = registry_key

    def __call__(self, request):
        request_db = RequestDB(request)
        request.add_finished_callback(request_db.cleanup)
        return request_db.session


class RequestDB(object):

    def __init__(self, request):
        self.request = request

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
            self._rollback()
        else:
            self._commit()

    def _rollback(self):
        self.session.rollback()
        self.maker.remove()

    def _commit(self):
        try:
            self.session.commit()
        finally:
            self.maker.remove()
