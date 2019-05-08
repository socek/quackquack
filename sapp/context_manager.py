from collections.abc import Iterable


class ContextManager(object):
    def __init__(self, application, values=[]):
        self.application = application
        self.values = values
        self.context = None

    def __enter__(self):
        ctx = self.application._enter_context()
        if not self.values:
            return ctx
        elif isinstance(self.values, str):
            return getattr(ctx, self.values)
        elif isinstance(self.values, Iterable):
            return [getattr(ctx, key) for key in self.values]
        else:
            raise AttributeError("Wrong argument type!")

    def __exit__(self, exc_type, exc_value, traceback):
        self.application._exit_context(exc_type, exc_value, traceback)
