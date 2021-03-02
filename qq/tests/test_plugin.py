from qq.plugin import Plugin


class TestPlugin:
    """
    Plugin does not do anything by itself. This is only a sanity check.
    """

    def test_plugin(self):
        plugin = Plugin()
        plugin.start('configurator')
        plugin.enter('application')
        plugin.exit('application', 'exc_type', 'exc_value', 'traceback')
