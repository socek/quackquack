class WithContext(object):
    def __init__(self, application, context_name='context', args=None):
        self.context_name = context_name
        self.application = application
        self.args = args or []

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            with self.application as context:
                if self.args:
                    for arg in self.args:
                        kwargs[arg] = getattr(context, arg)
                else:
                    kwargs[self.context_name] = context
                return fun(*args, **kwargs)
        return wrapper
