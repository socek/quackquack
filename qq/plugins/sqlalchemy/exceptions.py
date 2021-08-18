class SettingMissing(Exception):
    """
    Setting's key is missing.
    """
    _FORMAT = ("'{0}' key is needed for use '{1}' database in application")

    def __init__(self, key, name):
        super().__init__()
        self.key = key
        self.name = name

    def __str__(self):
        return self._FORMAT.format(self.key, self.name)
