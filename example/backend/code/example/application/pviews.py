from sapp import Decorator
from sapp.plugins.pyramid.views import RestfulView

from example import app
from example.application.models import Base
from example.application.models import Model


class SimpleView(RestfulView):
    @Decorator(app)
    def get(self, ctx):
        """
        List all active panels.
        """
        Base.metadata.create_all(ctx.dbsession_engine)
        first = ctx.dbsession.query(Model)[-1]
        key = first.key if first else None
        value = first.value if first else None
        return {"hello": True, "key": key, "value": value}


class CreateView(RestfulView):
    @Decorator(app, "dbsession")
    def get(self, dbsession):
        """
        List all active panels.
        """
        model = Model()
        model.key = "mykey"
        model.value = "myvalue"
        dbsession.add(model)
        dbsession.commit()
        return {"success": True, "uid": model.uid}
