class Driver(object):
    model = None

    def __init__(self, database):
        self.database = database

    def _query(self):
        return self.database.query(self.model)


class Query(Driver):

    def get_by_id(self, id):
        return self._query().filter(self.model.id == id).one()

    def list_all(self):
        return self._query().all()


class Command(Driver):

    def create(self, **kwargs):
        obj = self.model()
        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.database.add(obj)
        self.database.commit()
        return obj
