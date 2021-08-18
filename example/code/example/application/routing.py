from qq.plugins.pyramid.routing import Routing


class ExampleRouting(Routing):
    def make(self):
        self.add("example.application.pviews.SimpleView", "index", "/")
        self.add("example.application.pviews.CreateView", "create", "/create")
        self.add("example.application.pviews.TaskView", "task", "/task")
