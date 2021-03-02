from example import app
from example.application.models import Base
from example.application.models import Model
from example.tasks import input_value

from qq import Decorator
from qq.plugins.pyramid.views import RestfulView


class SimpleView(RestfulView):
    @Decorator(app)
    def get(self, ctx):
        """
        List all active panels.
        """
        Base.metadata.create_all(ctx.dbsession_engine)
        query = ctx.dbsession.query(Model)
        models = [model.to_dict() for model in query]
        return {"hello": True, "models": models}


class CreateView(RestfulView):
    @Decorator(app, "dbsession")
    def get(self, dbsession):
        """
        List all active panels.
        """
        model = Model()
        model.key = "pyramid"
        model.value = "myvalue"
        dbsession.add(model)
        dbsession.commit()
        return {"success": True, "uid": model.uid}


class TaskView(RestfulView):
    def get(self):
        input_value.delay("pyramid")
