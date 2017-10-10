
class WithDatabase(object):
    """
    Add database scope to the function.
    Default behavior is that this
    """

    def __init__(self, app, name='database', close_after_end=True):
        self.app = app
        self.name = name
        self.close_after_end = close_after_end

    @property
    def db(self):
        return self.app.dbs[self.name]

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            kwargs[self.name] = self.db.get_session()

            try:
                return fun(*args, **kwargs)
            finally:
                self.cleanup()

        return wrapper

    def cleanup(self):
        if self.close_after_end:
            self.db.close()
