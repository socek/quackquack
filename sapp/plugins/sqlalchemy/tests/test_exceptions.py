from sapp.plugins.sqlalchemy.exceptions import SettingMissing


class TestSettingMissing(object):
    def test_stringify(self):
        """
        SettingMissing should be able to format proper message.
        """
        assert str(SettingMissing('key', 'name')) == "'key' key is needed for use 'name' database in application"
