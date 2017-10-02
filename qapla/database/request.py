class RequestDBSessionGenerator(object):

    def __init__(self, registry_key):
        self.registry_key = registry_key

    def __call__(self, request):
        maker = request.registry[self.registry_key]
        self.session = maker()
        request.add_finished_callback(self.cleanup)
        return self.session

    def cleanup(self, request):
        if request.exception is not None:
            self.session.rollback()
        else:
            try:
                self.session.commit()
            except:
                self.session.rollback()
        self.session.close()
