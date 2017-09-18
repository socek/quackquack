class SettingMissing(Exception):
    """
    Setting's key is missing.
    """

    def __init__(self, key, description):
        self.key = key
        self.description = description
