class Plugin:
    def init(self, key: str):
        """
        Initialize the plguin during creating the plugins.
        key - key which is used in the Application.plugins dict for this plugin.
        """
        self.key = key

    def start(self, application):
        """
        This method will be called at the start of the Application. It will be
        called only once and the result will be set in the Application.globals.
        """

    def enter(self, application):
        """
        This method will be called when the Application will be used as context
        manager. This is the enter phase. Result will be pasted in the Context
        dict.
        """

    def exit(self, application, exc_type, exc_value, traceback):
        """
        This method will be called when the Application will be used as context
        manager. This is the exit phase.
        """
