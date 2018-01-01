class Context(object):
    def __init__(self, configurator):
        self.configurator = configurator

    def enter(self):
        for plugin in self.configurator.plugins:
            plugin.enter(self)

    def exit(self, exc_type, exc_value, traceback):
        for plugin in reversed(self.configurator.plugins):
            plugin.exit(self, exc_type, exc_value, traceback)
