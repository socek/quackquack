class WithContext(object):
    def __init__(self, application, context_name='context', args=None):
        self.context_name = context_name
        self.application = application
        self.args = args or []

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            with self.application as context:
                return self.fun_with_context(fun, context, args, kwargs)
        return wrapper

    def fun_with_context(self, fun, context, args, kwargs):
        if self.args:
            for arg in self.args:
                self.set_kwarg(kwargs, arg, getattr(context, arg))
        else:
            kwargs[self.context_name] = context
        return fun(*args, **kwargs)

    def set_kwarg(self, kwargs, arg, value):
        if arg not in kwargs:
            kwargs[arg] = value
