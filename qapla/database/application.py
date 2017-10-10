from qapla.app import Application

from qapla.database.plugin import DatabasePlugin


class DatabaseApplication(Application):

    def add_database_app(self, databases):
        """
        Add sqlalchemy database to the Application.
        """
        self.dbs = DatabasePlugin(self)
        for database in databases:
            self.dbs.add_database(database)
        self.dbs.add_to_app()

    def add_database_web(self):
        """
        Add sqlalchemy database to the pyramid app.
        """
        self.dbs.add_to_web()
