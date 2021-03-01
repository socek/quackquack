class ConfiguratorNotStartedError(RuntimeError):
    pass


class Context:
    def __init__(self, application):
        self.application = application
        self.values = {}
        self.token = None

    def enter(self):
        if not self.application.is_started:
            raise ConfiguratorNotStartedError(
                "Application is not started! Use Application.start(startpoint)"
            )
        try:
            return self.application.context.get()
        except LookupError:
            # I'm the first context, so I can return self.
            self.token = self.application.context.set(self)
            return self

    def exit(self, exc_type, exc_value, traceback):
        if self.token:
            for key, plugin in reversed(self.application.plugins.items()):
                if key in self.values:
                    plugin.exit(self, exc_type, exc_value, traceback)
            self.application.context.reset(self.token)

    def __getitem__(self, key):
        if key not in self.values:
            self.values[key] = self.application.plugins[key].enter(self)
        return self.values[key]

    def __enter__(self):
        return self.enter()

    def __exit__(self, exc_type, exc_value, traceback):
        return self.exit(exc_type, exc_value, traceback)
