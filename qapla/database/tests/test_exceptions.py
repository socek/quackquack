from mock import sentinel

from qapla.database.exceptions import SettingMissing


class TestSettingMissing(object):

    def test_init(self):
        """
        Sanity check.
        """
        error = SettingMissing(sentinel.key, sentinel.description)
        assert error.key == sentinel.key
        assert error.description == sentinel.description
