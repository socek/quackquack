from qapla.plugin import Plugin


class RoutingPlugin(Plugin):
    """
    Add routing to the pyramid app.
    """

    def __init__(self, routing_cls):
        self.routing_cls = routing_cls

    def start_plugin(self, configurator):
        self.configurator = configurator

    def start_web_plugin(self, pyramid):
        self.routing = self.routing_cls(pyramid, self.configurator.paths)
        self.routing.make()
