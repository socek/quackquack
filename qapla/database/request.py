class RequestDBSessionGenerator(object):

    def __call__(self, request):
        maker = request.registry.sessionmaker
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
                raise
        self.session.close()
