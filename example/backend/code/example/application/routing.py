from sapp.plugins.pyramid.routing import Routing


class ExampleRouting(Routing):
    def make(self):
        self.add("example.application.pviews.SimpleView", "index", "/")

