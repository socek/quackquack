from example import app
from example.application.models import Model
from example.tasks import input_value
from tornado.web import RequestHandler

from qq import Decorator


class MainHandler(RequestHandler):
    @Decorator(app, "dbsession")
    def get(self, dbsession):
        model = Model()
        model.key = "tornado"
        model.value = "myvalue"
        dbsession.add(model)
        dbsession.commit()
        self.write("Object created")


class TaskHandler(RequestHandler):
    def get(self):
        input_value.delay("tornado")
        self.write("Task started")
