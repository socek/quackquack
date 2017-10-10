class DatabasePlugin(object):

    def __init__(self, app):
        self.app = app
        self.databases = {}

    def add_database(self, database):
        """
        Add new database object to use in the application.
        """
        self.databases[database.name] = database

    def add_to_app(self):
        """
        Init all the provided databases.
        """
        for database in self.databases.values():
            database.add_to_app(self.app)

    def add_to_web(self):
        """
        Add all databases to request.
        """
        for database in self.databases.values():
            database.add_to_web()

    def __getitem__(self, name):
        return self.databases[name]
