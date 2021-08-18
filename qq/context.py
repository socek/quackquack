from qq import Application
from qq.errors import ApplicationNotStartedError


class Context:
    def __init__(self, application: Application):
        self.application = application
        self.values = {}
        self.token = None

    @property
    def globals(self):
        return self.application.globals

    @property
    def extra(self):
        return self.application.extra

    def __enter__(self):
        if not self.application.is_started:
            raise ApplicationNotStartedError(
                "Application is not started! Use Application.start(startpoint)"
            )
        try:
            return self.application.context.get()
        except LookupError:
            # I'm the first context, so I can return myself.
            self.token = self.application.context.set(self)
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.token:
            for key, plugin in reversed(self.application.plugins.items()):
                if key in self.values:
                    plugin.exit(self, exc_type, exc_value, traceback)
            self.application.context.reset(self.token)
            self.token = None

    def __getitem__(self, key: str):
        if key not in self.values:
            self.values[key] = self.application.plugins[key].enter(self)
        return self.values[key]
