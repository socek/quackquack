from collections.abc import Iterable


class Decorator(object):
    def __init__(self, application, values=[]):
        self.application = application
        self.values = values
        self.context = None

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            ctx = self.application._enter_context()
            kwargs = dict(kwargs)
            try:
                if self.values == []:
                    if "ctx" not in kwargs:
                        kwargs["ctx"] = ctx
                elif isinstance(self.values, str):
                    if self.values not in kwargs:
                        kwargs[self.values] = getattr(ctx, self.values)
                elif isinstance(self.values, Iterable):
                    for key in self.values:
                        if key not in kwargs:
                            kwargs[key] = getattr(ctx, key)
                else:
                    raise AttributeError("Wrong argument type!")
                return fun(*args, **kwargs)
            finally:
                # TODO: we probably need to pass here something
                self.application._exit_context(None, None, None)

        return wrapper
