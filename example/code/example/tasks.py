from example import app
from example.application.capp import cel
from example.application.models import Model

from qq import Decorator


@cel.task
@Decorator(app, "dbsession")
def input_value(value, dbsession):
    model = Model()
    model.key = "celery"
    model.value = value
    dbsession.add(model)
    dbsession.commit()
