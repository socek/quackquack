class Plugin(object):
    def init_plugin(self, configurator):
        pass

    def init_pyramid(self, pyramid):
        pass

    def enter(self, application):
        pass

    def exit(self, application, exc_type, exc_value, traceback):
        pass