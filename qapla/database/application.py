from qapla.app import Application

from qapla.database.plugin import DatabasePlugin


class DatabaseApplication(Application):

    def add_database_app(self):
        """
        Add sqlalchemy database to the Application.
        """
        self._db_plugin = DatabasePlugin(self)
        self._db_plugin.add_to_app()

    def add_database_web(self):
        """
        Add sqlalchemy database to the pyramid app.
        """
        self._db_plugin.add_to_web()
