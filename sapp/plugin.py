class Plugin(object):
    def start(self, configurator):
        """
        This method will be called at the start of the Configurator. It will be
        called only once per process start. configurator is an object where all
        the configuratation is stored.
        """

    def enter(self, application):
        """
        This method will be called when the Configurator will be used as context
        manager. This is the enter phase.
        """

    def exit(self, application, exc_type, exc_value, traceback):
        """
        This method will be called when the Configurator will be used as context
        manager. This is the exit phase.
        """
