class RequestDBSessionGenerator(object):

    def __init__(self, registry_key):
        self.registry_key = registry_key

    def __call__(self, request):
        self.session = self.create_session(request)
        request.add_finished_callback(self.cleanup)
        return self.session

    def create_session(self, request):
        return request.registry[self.registry_key]()

    def cleanup(self, request):
        if request.exception is not None:
            self._rollback()
        else:
            self._commit()

    def _rollback(self):
        self.session.rollback()
        print('closing! 1')
        self.session.close()

    def _commit(self):
        try:
            self.session.commit()
        finally:
            print('closing! 2')
            self.session.close()
