class SettingMissing(Exception):
    """
    Setting's key is missing.
    """

    def __init__(self, key, description):
        super().__init__()
        self.key = key
        self.description = description
