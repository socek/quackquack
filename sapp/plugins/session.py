from qapla.plugin import Plugin


class SessionPlugin(Plugin):
    """
    Add session mechanism to the pyramid app.
    """

    def __init__(self, session_factory_cls):
        self.session_factory_cls = session_factory_cls

    def start_plugin(self, configurator):
        self.settings = self.configurator.settings

    def start_web_plugin(self, pyramid):
        secret = self.settings['session_secret']
        session_factory = self.session_factory_cls(secret)
        pyramid.set_session_factory(session_factory)
